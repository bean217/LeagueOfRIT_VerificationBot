import discord


states = [
    'new',
    'name',
    'year',
    'discovery',
    'email',
    'done'
]


class User():
    def __init__(self, user: discord.Member):
        # user data
        self.user = user
        self.__state_index = 0

    @property
    def state(self):
        return states[self.__state_index]

    @property
    def is_complete(self):
        return self.__state_index == len(states)-1

    def next_state(self):
        if self.__state_index < len(states)-1:
            self.__state_index += 1


def main():
    test = User("ben")
    print("test")
    while not test.is_complete:
        print(test.state)
        test.next_state()

if __name__ == "__main__":
    main()