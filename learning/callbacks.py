from stable_baselines3.common.callbacks import CheckpointCallback

class StateCheckpointCallback(CheckpointCallback):
    def __init__(self, save_freq, save_path, name_prefix):
        super().__init__(save_freq=save_freq, save_path=save_path, name_prefix=name_prefix)

    def _on_step(self) -> bool:
        
        infos = self.locals["infos"]
        self.latest_states = []
        env_rewards = self.training_env.get_attr("total_reward")

        for i, info in enumerate(infos):
            if "game_state" in info:                
                info["game_state"]["total_reward"] = env_rewards[i]
                self.latest_states.append(info["game_state"])
        return True