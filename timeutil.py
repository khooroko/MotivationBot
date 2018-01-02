class TimeUtil:

    @staticmethod
    def is_valid_time(time_to_check):
        try:
            int(time_to_check)
            if not str.strip(time_to_check).__len__() == 4:
                return False
            if int(time_to_check[0:2]) > 23 or int(time_to_check[0:2]) < 0:
                return False
        except ValueError:
            return False

        return True

    @staticmethod
    def convert_string_to_time(string):
        return str(string)[0:2] + ":" + str(string)[2:4]

    @staticmethod
    def pad_to_two_digits(arg):
        if str(arg).__len__() < 2:
            return "0" + str(arg)
        else:
            return str(arg)