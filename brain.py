from commands import router
from planner import planner
from intent_dispatcher import dispatcher
from speech import speaker
from intent import intent_engine

class Brain:

    def process(self, command: str) -> bool:
        print(f"Brain received: '{command}'")

        # Fast path: exact/prefix commands
        result = router.route(command)

        if result:
            return True

        intent = intent_engine.detect(command)

        response = dispatcher.execute(intent)

        if response:
            speaker.speak(response)

        return True


brain = Brain()