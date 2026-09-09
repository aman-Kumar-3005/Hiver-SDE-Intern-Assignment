import unittest

from atlas_agent.data import Example
from atlas_agent.engine import SupportAgent


class SupportAgentTests(unittest.TestCase):
    def test_billing_is_classified_and_reply_does_not_invent_refund(self):
        agent = SupportAgent([Example("why was I charged twice", "billing_payment", "We checked the charge.")])
        prediction = agent.predict("I was charged twice this month")
        self.assertEqual(prediction.intent, "billing_payment")
        self.assertNotIn("refund", prediction.reply.lower())


    def test_unknown_is_escalated(self):
        agent = SupportAgent([Example("activate my sim", "sim_activation", "We can help.")])
        prediction = agent.predict("Tell me something unrelated")
        self.assertEqual(prediction.action, "escalate")