class Evaluator(object):

    LAST_RESULT = '^'

    def eval(self, form, env):
        result = form.eval(env)
        env[self.LAST_RESULT] = result
        return env
