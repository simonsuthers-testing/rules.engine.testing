from durable.lang import ruleset, post, when_all, m

# see https://pypi.org/project/durable-rules/
# https://github.com/jruizgit/rules/blob/master/docs/py/reference.md

with ruleset("test"):

    # antecedent
    @when_all(m.subject == "World")
    def say_hello(c):
        print(f"hello {c.m.subject}")

post("test", {"subject": "World"})