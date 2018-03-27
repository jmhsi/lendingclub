class ConfigData(object):

    def __init__(self, filename):
        cfg_parser = ConfigParser.ConfigParser()
        cfg_parser.optionxform = str
        cfg_parser.read(filename)
        self.investor_id = self.cast_num(
            cfg_parser.get('account_data', 'investor_id'))
        self.authKey = cfg_parser.get('account_data', 'authKey')
        self.reserve_cash = self.cast_num(
            cfg_parser.get('account_data', 'reserve_cash'))
        self.invest_amount = self.cast_num(
            cfg_parser.get('account_data', 'invest_amount'))
        if self.invest_amount < 25 or self.invest_amount % 25 != 0:
            raise RuntimeError(
                'Invalid investment amount specified in configuration file')
        self.portfolio_name = cfg_parser.get('account_data', 'portfolio_name')
        # criteriaOpts = cfg_parser.options(
        #     'LoanCriteria')  # Loan filtering criteria
        # self.criteria = {}
        # for opt in criteriaOpts:
        #     self.criteria[opt] = self.cast_num(
        #         cfg_parser.get('LoanCriteria', opt))

    def cast_num(self, val):
        try:
            i = int(val)
            return i
        except ValueError:
            try:
                d = decimal.Decimal(val)
                return d
            except decimal.InvalidOperation:
                return val
