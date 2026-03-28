# Smart-greenbin
Smart Green Bin system for AI hackathon. Citizens report garbage with photo and address, and system prioritizes cleaning.
import random

class GreenBinEnv:
    def __init__(self):
        self.bins = [random.randint(10, 100) for _ in range(5)]
        self.reports = []
        self.score = 0

    def reset(self):
        self.bins = [random.randint(10, 100) for _ in range(5)]
        self.reports = []
        self.score = 0
        return self.bins

    def report_issue(self, address):
        self.reports.append(address)
        return "Report Added"

    def step(self, action):
        if action == "clean_bin":
            idx = self.bins.index(max(self.bins))
            fill = self.bins[idx]

            if fill > 70:
                reward = 10
            else:
                reward = 5

            self.bins[idx] = 0

        elif action == "clean_report":
            if self.reports:
                self.reports.pop(0)
                reward = 15
            else:
                reward = -10

        self.score += reward
        return self.bins, self.reports, reward, self.score


env = GreenBinEnv()
env.reset()

print("Initial bins:", env.bins)

env.report_issue("Main Road")

for _ in range(3):
    state = env.step("clean_bin")
    print(state)
