import math


class Player:
    # Class attribute
    # The system constant, which constrains
    # the change in volatility over time.
    _tau = 0.5

    def getRating(self):
        return (self.__rating * 173.7178) + 1500

    def setRating(self, rating):
        self.__rating = (rating - 1500) / 173.7178

    rating = property(getRating, setRating)

    def getRd(self):
        return self.__rd * 173.7178

    def setRd(self, rd):
        self.__rd = rd / 173.7178

    rd = property(getRd, setRd)

    def __init__(self, rating=1500, rd=350, vol=0.06):
        # For testing purposes, preload the values
        # assigned to an unrated player.
        self.setRating(rating)
        self.setRd(rd)
        self.vol = vol

    def _preRatingRD(self):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.

        preRatingRD() -> None

        """
        self.__rd = math.sqrt(math.pow(self.__rd, 2) + math.pow(self.vol, 2))

    def update_player(self, rating_list, RD_list, outcome_list):
        """ Calculates the new rating and rating deviation of the player.

        update_player(list[int], list[int], list[bool]) -> None

        """
        # Convert the rating and rating deviation values for internal use.
        rating_list = [(x - 1500) / 173.7178 for x in rating_list]
        RD_list = [x / 173.7178 for x in RD_list]

        v = self._v(rating_list, RD_list)
        self.vol = self._newVol(rating_list, RD_list, outcome_list, v)
        self._preRatingRD()

        self.__rd = 1 / math.sqrt((1 / math.pow(self.__rd, 2)) + (1 / v))

        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * \
                       (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        self.__rating += math.pow(self.__rd, 2) * tempSum

    # step 5
    def _newVol(self, rating_list, RD_list, outcome_list, v):
        """ Calculating the new volatility as per the Glicko2 system.

        _newVol(list, list, list, float) -> float

        """
        # step 1
        a = math.log(self.vol ** 2)
        eps = 0.000001
        A = a

        # step 2
        B = None
        delta = self._delta(rating_list, RD_list, outcome_list, v)
        tau = self._tau
        if (delta ** 2) > ((self.__rd ** 2) + v):
            B = math.log(delta ** 2 - self.__rd ** 2 - v)
        else:
            k = 1
            while self._f(a - k * math.sqrt(tau ** 2), delta, v, a) < 0:
                k = k + 1
            B = a - k * math.sqrt(tau ** 2)

        # step 3
        fA = self._f(A, delta, v, a)
        fB = self._f(B, delta, v, a)

        # step 4
        while math.fabs(B - A) > eps:
            # a
            C = A + ((A - B) * fA) / (fB - fA)
            fC = self._f(C, delta, v, a)
            # b
            if fC * fB <= 0:
                A = B
                fA = fB
            else:
                fA = fA / 2.0
            # c
            B = C
            fB = fC

        # step 5
        return math.exp(A / 2)

    def _f(self, x, delta, v, a):
        ex = math.exp(x)
        num1 = ex * (delta ** 2 - self.__rating ** 2 - v - ex)
        denom1 = 2 * ((self.__rating ** 2 + v + ex) ** 2)
        return (num1 / denom1) - ((x - a) / (self._tau ** 2))

    def _delta(self, rating_list, RD_list, outcome_list, v):
        """ The delta function of the Glicko2 system.

        _delta(list, list, list) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        return v * tempSum

    def _v(self, rating_list, RD_list):
        """ The v function of the Glicko2 system.

        _v(list[int], list[int]) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self._E(rating_list[i], RD_list[i])
            tempSum += math.pow(self._g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / tempSum

    def _E(self, p2rating, p2RD):
        """ The Glicko E function.

        _E(int) -> float

        """
        return 1 / (1 + math.exp(-1 * self._g(p2RD) * \
                                 (self.__rating - p2rating)))

    def _g(self, RD):
        """ The Glicko2 g(RD) function.

        _g() -> float

        """
        return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))

    def did_not_compete(self):
        """ Applies Step 6 of the algorithm. Use this for
        players who did not compete in the rating period.

        did_not_compete() -> None

        """
        self._preRatingRD()


def calculate_odds(a,b):
    diff = a - b
    x = diff / 160
    win_percent = 1 / (1 + math.pow(math.e, -x))
    win_percent = win_percent * 100
    return win_percent


def calculate_margin(total_profit):
    x = total_profit / 600
    margin = (1 / (1 + math.pow(math.e, x))) / 10
    return margin
