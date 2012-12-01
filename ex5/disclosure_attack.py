import sys
from string import ascii_lowercase
from parse_rounds import parseRounds

numUsers = 260
num_rounds = 256
users_per_round = 32
usersToIndex = {}
indexToUsers = {}

def findFriends(send_rounds, rec_rounds, user):
    """
    Returns the friends which the given user has as determined from the
    data from send and receive rounds using an extended statistical
    disclosure attack.
    """
    b_traffic = [0] * 260

    rounds_not_in = 0
    total_messages = 0

    observations = [0] * 260

    num_rounds = float(len(send_rounds))

    for index,send_round in enumerate(send_rounds):
        if user in send_round:
            for s_user in rec_rounds[index]:
                observations[getIndexForUser(s_user)] += 1.0/num_rounds

            total_messages += send_round.count(user)
        else:
            for r_user in rec_rounds[index]:
                b_traffic[getIndexForUser(r_user)] += 1.0/users_per_round

            rounds_not_in += 1

    if rounds_not_in == num_rounds:
        return []

    print("{} not in {} send rounds".format(user, rounds_not_in))
    b_traffic[:] = map(lambda traffic: traffic / float(rounds_not_in), b_traffic)

    user_avg_msgs = total_messages / float(num_rounds)
    b_traffic[:] = map(lambda traffic: (users_per_round - user_avg_msgs) * traffic, b_traffic)

    user_recipient_prob = []
    for i in range(len(observations)):
        obs = observations[i]
        traffic = b_traffic[i]
        user_recipient_prob.append((obs - traffic) / float(user_avg_msgs))

    friends = []
    for index,val in enumerate(user_recipient_prob):
        if val > 0:
            friends.append(getUserForIndex(index))

    return friends


def buildUserIndexes():
    lowest_char = ord(ascii_lowercase[0])
    for char in ascii_lowercase:
        for i in range(10):
            user = char + str(i)
            index = ((ord(char)*10) + i) - (lowest_char * 10)

            usersToIndex[user] = index
            indexToUsers[index] = user

def getIndexForUser(user):
    return usersToIndex[user]

def getUserForIndex(index):
    return indexToUsers[index]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} [round file]".format(sys.argv[0]))
        sys.exit(1)

    buildUserIndexes()

    send_rounds, receive_rounds = parseRounds(sys.argv[1])

    for user,index in usersToIndex.items():
        friends = findFriends(send_rounds, receive_rounds, user)
        print("{} -> {}".format(user, friends))


