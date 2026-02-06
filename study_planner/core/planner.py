"""
Study session orchestration and workflow management.

This module provides the StudyPlanner class which coordinates the entire
study session workflow, managing state transitions, timer lifecycle,
notifications, and data persistence.
"""

from typing import Optional
from study_planner.core.state import SessionState
from study_planner.core.timer import TimerEngine
from study_planner.core.plans import StudyPlan
from study_planner.core.notifier import Notifier
from study_planner.data.history import HistoryManager
from study_planner.data.statistics import StatisticsTracker


class StudyPlanner:
    """
    Orchestrates study session workflow and state management.
    
    Coordinates timer engine, state machine, notifications, history tracking,
    and statistics recording. Manages the complete lifecycle of a study session
    from start to completion or interruption.
    """
    
    def __init__(
        self,
        notifier: Notifier,
        history: HistoryManager,
        stats: StatisticsTracker
    ):
        """
        Initialize StudyPlanner with dependencies.
        
        Args:
            notifier: Notifier instance for phase transition alerts
            history: HistoryManager instance for tracking configurations
            stats: StatisticsTracker instance for recording session data
        """
        self._notifier = notifier
        self._history = history
        self._stats = stats
        
        # Session state
        self._current_state = SessionState.IDLE
        self._current_plan: Optional[StudyPlan] = None
        self._current_timer: Optional[TimerEngine] = None
        
        # Cycle tracking
        self._current_cycle = 0
        self._total_cycles = 0
        
        # Time tracking for statistics
        self._session_start_time = 0
        self._total_study_time = 0
        
        # Track state before pause for resume
        self._state_before_pause: Optional[SessionState] = None
    
    def start_session(self, plan: StudyPlan) -> None:
        """
        Begin a new study session with the given plan.
        
        Initializes session state to STUDY, starts the study timer,
        and sets up cycle tracking.
        
        Args:
            plan: StudyPlan configuration for the session
            
        Raises:
            RuntimeError: If a session is already active
        """
        if self._current_state != SessionState.IDLE:
            raise RuntimeError("Cannot start session: a session is already active")
        
        self._current_plan = plan
        self._current_cycle = 1
        self._total_cycles = plan.cycles
        self._total_study_time = 0
        
        # Add to history immediately when starting
        self._history.add_entry(plan)
        
        # Transition to STUDY state and start study timer
        self._current_state = SessionState.STUDY
        self._start_study_phase()
    
    def pause_session(self) -> None:
        """
        Pause the current session.
        
        Transitions from STUDY, BREAK, or LONG_BREAK state to PAUSED state,
        preserving remaining time in the timer.
        
        Raises:
            RuntimeError: If no session is active or session is not pausable
        """
        if self._current_state not in (SessionState.STUDY, SessionState.BREAK, SessionState.LONG_BREAK):
            raise RuntimeError("Cannot pause: no active phase to pause")
        
        # Save current state before pausing
        self._state_before_pause = self._current_state
        
        if self._current_timer:
            self._current_timer.pause()
        
        self._current_state = SessionState.PAUSED
    
    def resume_session(self) -> None:
        """
        Resume a paused session.
        
        Returns to the previous state (STUDY, BREAK, or LONG_BREAK) and
        continues the countdown from where it was paused.
        
        Raises:
            RuntimeError: If session is not in PAUSED state
        """
        if self._current_state != SessionState.PAUSED:
            raise RuntimeError("Cannot resume: session is not paused")
        
        if self._current_timer:
            self._current_timer.resume()
        
        # Restore the state from before pause
        if self._state_before_pause:
            self._current_state = self._state_before_pause
            self._state_before_pause = None
        else:
            # Fallback to STUDY if no previous state tracked
            self._current_state = SessionState.STUDY
    
    def stop_session(self) -> None:
        """
        Stop and abandon the current session.
        
        Transitions to IDLE state, stops the timer, records the session
        as interrupted in statistics, and cleans up session state.
        """
        if self._current_state == SessionState.IDLE:
            return
        
        # Stop the timer if running
        if self._current_timer:
            self._current_timer.stop()
            self._current_timer = None
        
        # Record interrupted session if we had a plan
        if self._current_plan:
            # Calculate partial study time (in minutes)
            partial_minutes = self._total_study_time // 60
            self._stats.record_interrupted_session(self._current_plan, partial_minutes)
        
        # Reset to IDLE state
        self._current_state = SessionState.IDLE
        self._current_plan = None
        self._current_cycle = 0
        self._total_cycles = 0
        self._total_study_time = 0
    
    def skip_current_phase(self) -> None:
        """
        Skip to the next phase (study/break).
        
        Immediately ends the current timer and transitions to the next
        phase in the session flow.
        
        Raises:
            RuntimeError: If no session is active
        """
        if self._current_state not in (SessionState.STUDY, SessionState.BREAK, SessionState.LONG_BREAK):
            raise RuntimeError("Cannot skip: no active phase")
        
        # Stop current timer
        if self._current_timer:
            self._current_timer.stop()
            self._current_timer = None
        
        # Trigger the phase transition logic
        self._on_phase_complete()
    
    def get_current_state(self) -> SessionState:
        """
        Get the current session state.
        
        Returns:
            Current SessionState
        """
        return self._current_state
    
    def get_current_plan(self) -> Optional[StudyPlan]:
        """
        Get the active study plan.
        
        Returns:
            Current StudyPlan if a session is active, None otherwise
        """
        return self._current_plan
    
    def can_modify_plan(self) -> bool:
        """
        Check if plan modification is allowed.
        
        Plan modification is only allowed when in IDLE or COMPLETED state.
        
        Returns:
            True if plan can be modified, False otherwise
        """
        return self._current_state in (SessionState.IDLE, SessionState.COMPLETED)
    
    def _start_study_phase(self) -> None:
        """
        Start a study phase.
        
        Internal method to initialize and start the study timer.
        """
        if not self._current_plan:
            return
        
        duration_seconds = self._current_plan.study_minutes * 60
        
        self._current_timer = TimerEngine(
            duration_seconds=duration_seconds,
            on_tick=self._on_timer_tick,
            on_finish=self._on_phase_complete
        )
        
        self._current_timer.start()
        self._notifier.notify_study_start()
    
    def _start_break_phase(self) -> None:
        """
        Start a break phase.
        
        Internal method to initialize and start the break timer.
        """
        if not self._current_plan:
            return
        
        duration_seconds = self._current_plan.break_minutes * 60
        
        self._current_timer = TimerEngine(
            duration_seconds=duration_seconds,
            on_tick=self._on_timer_tick,
            on_finish=self._on_phase_complete
        )
        
        self._current_timer.start()
        self._notifier.notify_break_start()
    
    def _start_long_break_phase(self) -> None:
        """
        Start a long break phase.
        
        Internal method to initialize and start the long break timer.
        """
        if not self._current_plan:
            return
        
        duration_seconds = self._current_plan.long_break_minutes * 60
        
        self._current_timer = TimerEngine(
            duration_seconds=duration_seconds,
            on_tick=self._on_timer_tick,
            on_finish=self._on_phase_complete
        )
        
        self._current_timer.start()
        self._notifier.notify_long_break_start()
    
    def _on_timer_tick(self, remaining_seconds: int) -> None:
        """
        Callback for timer tick events.
        
        Called every second by the timer engine. Can be used for
        UI updates or other periodic actions.
        
        Args:
            remaining_seconds: Seconds remaining in current phase
        """
        # Track study time for statistics
        if self._current_state == SessionState.STUDY:
            # Increment by 1 second
            self._total_study_time += 1
    
    def _on_phase_complete(self) -> None:
        """
        Callback for phase completion.
        
        Handles state transitions when a timer completes. Implements
        the session flow logic with cycle tracking.
        """
        if not self._current_plan:
            return
        
        # Clean up current timer
        self._current_timer = None
        
        # Determine next state based on current state
        if self._current_state == SessionState.STUDY:
            # Study phase completed, transition to break
            self._current_state = SessionState.BREAK
            self._start_break_phase()
            
        elif self._current_state == SessionState.BREAK:
            # Break phase completed, check if more cycles remain
            if self._current_cycle < self._total_cycles:
                # More cycles remain, go back to study
                self._current_cycle += 1
                self._current_state = SessionState.STUDY
                self._start_study_phase()
            else:
                # All cycles complete, check for long break
                if self._current_plan.long_break_minutes > 0:
                    self._current_state = SessionState.LONG_BREAK
                    self._start_long_break_phase()
                else:
                    # No long break, session complete
                    self._complete_session()
        
        elif self._current_state == SessionState.LONG_BREAK:
            # Long break completed, session complete
            self._complete_session()
    
    def _complete_session(self) -> None:
        """
        Complete the session successfully.
        
        Transitions to COMPLETED state, records session in statistics,
        and persists data immediately.
        """
        self._current_state = SessionState.COMPLETED
        
        if self._current_plan:
            # Calculate actual study time in minutes
            actual_study_minutes = self._total_study_time // 60
            
            # Record completed session in statistics
            self._stats.record_completed_session(self._current_plan, actual_study_minutes)
            
            # History was already added in start_session(), no need to add again
            
            # Notify user
            self._notifier.notify_session_complete()
        
        # Clean up
        self._current_timer = None
