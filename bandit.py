# bandit.py
from numpy.random import choice, random

from bandit.services import UserService, BanditArmService, BanditArmMembershipService

# Pricing bandit is a terrible name for the app.
class PricingArmCollection(object):
    def __init__(self):
        self.experiment_name = "pricing"

    @property
    def arms(self):
        return BanditArm.objects.filter(
            experiment=self.experiment_name
        ).all()


class PricingArmAssigner(object):
    def __init__(self, organization):
        self.object = organization
        self.pricing_arm_collection = PricingArmCollection().arms
        self.bandit = PricingBandit(0.1, self.pricing_arm_collection)

    def assign_arm(self):
        if not self.object.belongs_to(self.pricing_arm_collection):
            ArmMembership(arm=self.chosen_arm,
                content_type=self.object_type,
                object_id=self.object_id,
            ).save()

    @property
    def chosen_arm(self):
        return self.bandit.suggest_arm()

    @property
    def object_type(self):
        return ContentType.objects.get_for_model(self.object)

    @property
    def object_id(self):
        return self.object.id

def create_epsilon_bandit(arms):
    selector = EpsilonArmSelector(0.10)

    return EpsilonBandit(selector, arms)

class EpsilonBandit(object):
    """
        arm_types are options, similar to groups in split tests
    """

    def __init__(self, selector, arms):
        self.selector = selector
        self.arms = arms

    def suggest_arm(self):
        if self.selector.exploit():
            return self.best_arm
        else:
            # return random arm
            return self.selector.select(self.arms)

    @property
    def best_arm(self):
        rates = dict(
            (arm, PricingArmSuccessRate(arm).rate)
            for arm in self.arms
        )

        return max(rates, key=rates.get)


class EpsilonArmSelector(object):
    def __init__(self, epsilon):
        self.epsilon = epsilon

    def exploit(self):
        return random() > self.epsilon

    def select(self, arms):
        return choice(arms)


class PricingArmSuccessRate(object):
    """
        PricingArmSuccessRate(arm).rate
    """
    def __init__(self, arm):
        self.arm = arm

    @property
    def reward(self):
        return PricingReward(self.arm).count

    @property
    def rate(self):
        try:
            return float(self.reward)/self.completed_experiments
        except ZeroDivisionError:
            # Since we haven't tried the experiment
            # then we should be using it, hence
            # the value is 1 (high performance)
            return 1

    @property
    def completed_experiments(self):
        # TODO: return the total number of times this
        # arm was presented.
        return 0


# YES, by in large, we've just set-up
# two classes, one serves as the numerator
# the other as a denominator. But abstraction!

class PricingReward(object):
    """
        TourReward(arm).count
    """
    def __init__(self, arm):
        self.arm = arm

    @property
    def count(self):
        # TODO: return the number of times this arm
        # was selected, or 'returned a reward' after
        # it was presented
        return 0

class BanditExperiments(object):
    """
        BanditExperiments("forced").count
    """
    def __init__(self, arm):
        self.arm = arm

    @property
    def count(self):
        # ArmMembership().count()
        return 0