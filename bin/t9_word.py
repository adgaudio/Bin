"""
Implements the T9 Word algorithm in python using a Prefix Tree (aka Trie)

if n=length of input sequence, algorithm is O(min(3**n))
size of the Trie is roughly the avg children per node * height
  (height is maximum length word in your dictionary)
  (# children per node is number of words that begin with the
     prefix at that node
"""

# map keypad numbers to the alphabet
n_to_s = {2: ['a','b','c'], 3: ['d','e','f'], 4: ['g','h','i'], 5: ['j','k','l'],
          6: ['m','n','o'], 7: ['p','q','r','s'], 8: ['t','u','v'], 
          9: ['w','x','y','z'] }

# a pre-populated Trie of english words.  I have a limited vocabulary
dct = {'c':
        {'a': {'t':{},
               'b':{},
               'r':{}
               },
         'u':{'t':{},
              'b':{}
              },
         }
       }

def t9(nums):
    words = []
    def recursively_build_words(nums, dct, word=""):
        if len(nums) == 0:
            words.append(word)
            return
        number = nums[0]
        letters = n_to_s[number]
        for letter in letters:
            if letter in dct:
                recursively_build_words(nums[1:], dct[letter], word+letter)
    recursively_build_words(nums, dct=dct)
    return words

print t9([2,2,2])
