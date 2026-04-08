"""
undo_manager.py
Σύστημα αναίρεσης ενεργειών (Undo System) — undo/redo functionality.
"""

import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Action:
    """Αναπαράσταση μιας αναίρεσης-ικανής ενέργειας."""
    name: str  # Όνομα ενέργειας (π.χ. "Add Sample")
    undo_fn: Callable  # Συνάρτηση αναίρεσης
    redo_fn: Callable  # Συνάρτηση επανάληψης
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict = field(default_factory=dict)  # Δεδομένα για debugging


class UndoManager:
    """Διαχειρίζεται την αναίρεση και επανάληψη ενεργειών."""
    
    def __init__(self, max_stack_size: int = 20):
        self.undo_stack: List[Action] = []
        self.redo_stack: List[Action] = []
        self.max_stack_size = max_stack_size
    
    def record_action(self, action: Action):
        """Καταγράφει μια ενέργεια που μπορεί να αναιρεθεί."""
        self.undo_stack.append(action)
        
        # Περιορίζει το μέγεθος του stack
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        
        # Καθαρίζει το redo stack όταν καταγράφεται νέα ενέργεια
        self.redo_stack.clear()
    
    def undo(self) -> tuple[bool, str]:
        """
        Αναιρεί την τελευταία ενέργεια.
        Returns: (success, message)
        """
        if not self.undo_stack:
            return False, "Δεν υπάρχουν ενέργειες προς αναίρεση"
        
        try:
            action = self.undo_stack.pop()
            action.undo_fn()
            self.redo_stack.append(action)
            return True, f"Αναίρεση: {action.name}"
        except Exception as e:
            self.undo_stack.append(action)  # Επαναφέρει την ενέργεια αν αποτύχει
            return False, f"Σφάλμα αναίρεσης: {str(e)}"
    
    def redo(self) -> tuple[bool, str]:
        """
        Επαναλαμβάνει την τελευταία αναιρεθείσα ενέργεια.
        Returns: (success, message)
        """
        if not self.redo_stack:
            return False, "Δεν υπάρχουν ενέργειες προς επανάληψη"
        
        try:
            action = self.redo_stack.pop()
            action.redo_fn()
            self.undo_stack.append(action)
            return True, f"Επανάληψη: {action.name}"
        except Exception as e:
            self.redo_stack.append(action)  # Επαναφέρει την ενέργεια αν αποτύχει
            return False, f"Σφάλμα επανάληψης: {str(e)}"
    
    def can_undo(self) -> bool:
        """Ελέγχει αν είναι δυνατή η αναίρεση."""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Ελέγχει αν είναι δυνατή η επανάληψη."""
        return len(self.redo_stack) > 0
    
    def get_undo_text(self) -> str:
        """Λαμβάνει κείμενο για το undo button."""
        if not self.undo_stack:
            return "Undo"
        return f"Undo: {self.undo_stack[-1].name}"
    
    def get_redo_text(self) -> str:
        """Λαμβάνει κείμενο για το redo button."""
        if not self.redo_stack:
            return "Redo"
        return f"Redo: {self.redo_stack[-1].name}"
    
    def clear(self):
        """Καθαρίζει όλα τα stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_history(self) -> Dict:
        """Επιστρέφει ολόκληρο την ιστορία για debugging."""
        return {
            "undo_count": len(self.undo_stack),
            "redo_count": len(self.redo_stack),
            "undo_stack": [
                {
                    "name": a.name,
                    "timestamp": a.timestamp,
                    "data": a.data
                }
                for a in self.undo_stack
            ],
            "redo_stack": [
                {
                    "name": a.name,
                    "timestamp": a.timestamp,
                    "data": a.data
                }
                for a in self.redo_stack
            ]
        }
