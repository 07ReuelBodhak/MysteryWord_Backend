words = [
    # Pets
    "dog", "cat", "rabbit", "hamster", "parrot", "fish", "turtle", "guinea pig",

    # Farm animals
    "cow", "buffalo", "goat", "sheep", "horse", "donkey", "pig", "hen", "rooster", "duck",

    # Wild animals
    "lion", "tiger", "elephant", "leopard", "cheetah", "bear", "wolf", "fox", "deer", "zebra",
    "giraffe", "rhinoceros", "hippopotamus", "monkey", "gorilla", "chimpanzee", "kangaroo",
    "panda", "camel", "crocodile", "alligator", "snake", "lizard", "frog",

    # Birds
    "sparrow", "pigeon", "crow", "eagle", "hawk", "falcon", "owl", "peacock", "parakeet",
    "canary", "woodpecker", "seagull", "swan", "duckling", "goose", "turkey", "vulture",
    "flamingo", "penguin", "ostrich",

    # Sea animals
    "shark", "whale", "dolphin", "octopus", "squid", "crab", "lobster", "starfish",
    "seahorse", "jellyfish",

    # Fruits
    "apple", "banana", "orange", "mango", "grapes", "pineapple", "watermelon",
    "papaya", "guava", "pear", "peach", "plum", "cherry", "strawberry",
    "blueberry", "raspberry", "pomegranate", "kiwi", "lemon", "lime",
    "coconut", "fig", "dates", "avocado",

    # Objects (daily life)
    "chair", "table", "bed", "sofa", "cup", "plate", "spoon", "fork", "knife",
    "bottle", "phone", "laptop", "computer", "keyboard", "mouse", "monitor",
    "television", "remote", "fan", "light", "bulb", "clock", "watch",
    "bag", "wallet", "shoes", "shirt", "pants", "jacket", "cap",
    "book", "notebook", "pen", "pencil", "eraser", "marker",
    "door", "window", "mirror", "camera",

    # Famous sports persons
    "Messi", "Ronaldo", "Neymar", "Mbappe", "Virat Kohli", "MS Dhoni", "Sachin Tendulkar",
    "Rohit Sharma", "Serena Williams", "Roger Federer", "Rafael Nadal",
    "LeBron James", "Michael Jordan", "Usain Bolt",

    # Actors
    "Leonardo DiCaprio", "Brad Pitt", "Tom Cruise", "Robert Downey Jr",
    "Johnny Depp", "Will Smith", "Dwayne Johnson", "Chris Evans",
    "Shah Rukh Khan", "Salman Khan", "Aamir Khan", "Akshay Kumar",

    # Singers
    "Michael Jackson", "Taylor Swift", "Ariana Grande", "Justin Bieber",
    "Ed Sheeran", "Drake", "The Weeknd", "Eminem",
    "Beyonce", "Rihanna"
]

def get_word():
    import random
    return random.choice(words)