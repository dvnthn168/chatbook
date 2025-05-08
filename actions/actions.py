from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionCheckSufficientFunds(Action):
    def name(self) -> Text:
        return "action_human_handoff"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        confirm = tracker.get_slot("request_human_handoff")

        if confirm is True:
            dispatcher.utter_message(text="Đang kết nối bạn với nhân viên tư vấn...")
            dispatcher.utter_message(json_message={"handoff": True})
        elif confirm is False:
            dispatcher.utter_message(response="utter_human_handoff_cancelled")
            dispatcher.utter_message(json_message={"handoff": False})
        else:
            dispatcher.utter_message(text="Tôi chưa rõ bạn có muốn kết nối hay không.")
            dispatcher.utter_message(json_message={"handoff": None})

        
        return [SlotSet("confirm_human_handoff", has_sufficient_funds)]
