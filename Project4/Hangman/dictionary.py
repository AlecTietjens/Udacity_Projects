from random import randint

words = ["jazziest",
         "quizzing",
         "fuzziest",
         "fizzling",
         "puppying",
         "whizzing",
         "jammiest",
         "babbling",
         "bubbling",
         "quizzers",
         "bowwowed",
         "muzzling",
         "acres",
         "adult",
         "attempt",
         "calm",
         "habit",
         "happily",
         "image",
         "relationship"]

def get_random_word():
    return words[randint(0, len(words) - 1)]