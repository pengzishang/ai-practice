from config.setting import settings
from agents.agent import Agent
def main():
    agent = Agent()
    result = agent.chat("Beijing and Shanghai")
    print(result)
if __name__ == "__main__":
    main()
