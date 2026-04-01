from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import Dict, Any

app = FastAPI(title="Space Colony Survival AI - OpenEnv")

class SpaceColonySurvivalEnv:
    def __init__(self, difficulty: str = "medium", max_steps: int = 1000, seed: int = None):
        assert difficulty in ["easy", "medium", "hard"]
        self.difficulty = difficulty
        self.max_steps = max_steps
        if seed is not None:
            np.random.seed(seed)

        self.configs = {
            "easy": {"oxygen": 150.0, "food": 150.0, "power": 150.0, "hazard_intensity": 0.20},
            "medium": {"oxygen": 100.0, "food": 100.0, "power": 100.0, "hazard_intensity": 0.40},
            "hard": {"oxygen": 60.0, "food": 60.0, "power": 60.0, "hazard_intensity": 0.65}
        }
        self.action_meanings = {0: "produce_oxygen", 1: "grow_food", 2: "generate_power", 3: "stabilize_system"}
        self.reset()

    def reset(self):
        config = self.configs[self.difficulty]
        self.oxygen = config["oxygen"]
        self.food = config["food"]
        self.power = config["power"]
        self.hazard_intensity = config["hazard_intensity"]
        self.time_step = 0
        self.survival_score = 0.0
        return self.state()

    def step(self, action: int):
        if action not in [0, 1, 2, 3]:
            raise ValueError("Action must be 0-3")

        # Agent action with trade-offs
        if action == 0:      # produce_oxygen
            self.oxygen += 28.0
            self.power -= 13.0
            self.food -= 4.0
        elif action == 1:    # grow_food
            self.food += 28.0
            self.power -= 13.0
            self.oxygen -= 9.0
        elif action == 2:    # generate_power
            self.power += 28.0
            self.oxygen -= 9.0
            self.food -= 9.0
        elif action == 3:    # stabilize_system
            self.hazard_intensity = max(0.0, self.hazard_intensity - 0.28)
            self.oxygen -= 6.0
            self.food -= 6.0
            self.power -= 11.0

        # Natural consumption
        self.oxygen -= 11.0
        self.food -= 11.0
        self.power -= 11.0

        self.oxygen = max(0.0, self.oxygen)
        self.food = max(0.0, self.food)
        self.power = max(0.0, self.power)

        # Random hazards (scaled by intensity)
        if np.random.rand() < self.hazard_intensity:
            if np.random.rand() < 0.5:  # meteor strike
                damage = np.random.uniform(22.0, 42.0)
                self.oxygen -= damage
                self.food -= damage
                self.power -= damage
            else:  # system failure
                damage = np.random.uniform(32.0, 58.0)
                target = np.random.choice([0, 1, 2])
                if target == 0:
                    self.oxygen -= damage
                elif target == 1:
                    self.food -= damage
                else:
                    self.power -= damage

        self.oxygen = max(0.0, self.oxygen)
        self.food = max(0.0, self.food)
        self.power = max(0.0, self.power)

        # Environment gets harsher over time
        self.hazard_intensity = min(1.0, self.hazard_intensity + 0.006)

        # Reward calculation
        min_res = min(self.oxygen, self.food, self.power)
        avg_res = (self.oxygen + self.food + self.power) / 3.0

        if min_res <= 0.0:
            reward = -250.0
            done = True
        else:
            reward = 4.0 + avg_res * 0.12 + (min_res / 8.0)
            done = False

        self.survival_score += max(0.0, avg_res * (1.0 - self.hazard_intensity * 0.5) / 5.0)

        self.time_step += 1
        if self.time_step >= self.max_steps:
            done = True
            reward += 800.0

        return self.state(), reward, done, {"action": self.action_meanings[action]}

    def state(self) -> Dict:
        return {
            "oxygen_level": round(self.oxygen, 2),
            "food_level": round(self.food, 2),
            "power_level": round(self.power, 2),
            "current_time_step": self.time_step,
            "hazard_intensity": round(self.hazard_intensity, 3),
            "survival_score": round(self.survival_score, 2)
        }


# Global environment
env = None

class StepRequest(BaseModel):
    action: int

@app.post("/reset")
async def reset_endpoint() -> Dict:
    global env
    env = SpaceColonySurvivalEnv(difficulty="medium")
    return env.state()

@app.post("/step")
async def step_endpoint(request: StepRequest) -> Dict[str, Any]:
    global env
    if env is None:
        raise HTTPException(status_code=400, detail="Call /reset first")
    state, reward, done, info = env.step(request.action)
    return {"state": state, "reward": reward, "done": done, "info": info}

@app.get("/state")
async def state_endpoint() -> Dict:
    global env
    if env is None:
        raise HTTPException(status_code=400, detail="Call /reset first")
    return env.state()

@app.get("/health")
async def health():
    return {"status": "healthy"}