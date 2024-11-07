import tkinter as tk
from tkinter import ttk

train_data = 'markov_chain.txt'

first_possible_words = {}
second_possible_words = {}
transitions = {}

def expandDict(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)

def get_next_probability(given_list):   # returns dictionary
    probability_dict = {}
    given_list_length = len(given_list)
    for item in given_list:
        probability_dict[item] = probability_dict.get(item, 0) + 1
    for key, value in probability_dict.items():
        probability_dict[key] = value / given_list_length
    return probability_dict

def trainMarkovModel():
    for line in open(train_data):
        tokens = line.rstrip().lower().split()
        tokens_length = len(tokens)
        for i in range(tokens_length):
            token = tokens[i]
            if i == 0:
                first_possible_words[token] = first_possible_words.get(token, 0) + 1
            else:
                prev_token = tokens[i - 1]
                if i == tokens_length - 1:
                    expandDict(transitions, (prev_token, token), 'END')
                if i == 1:
                    expandDict(second_possible_words, prev_token, token)
                else:
                    prev_prev_token = tokens[i - 2]
                    expandDict(transitions, (prev_prev_token, prev_token), token)
    
    first_possible_words_total = sum(first_possible_words.values())
    for key, value in first_possible_words.items():
        first_possible_words[key] = value / first_possible_words_total
        
    for prev_word, next_word_list in second_possible_words.items():
        second_possible_words[prev_word] = get_next_probability(next_word_list)
        
    for word_pair, next_word_list in transitions.items():
        transitions[word_pair] = get_next_probability(next_word_list)

def next_word(tpl):
    if isinstance(tpl, str):   # it is first word of string.. return from second word
        d = second_possible_words.get(tpl)
        if d is not None:
            return list(d.keys())
    if isinstance(tpl, tuple): # incoming words are combination of two words.. find next word now based on transitions
        d = transitions.get(tpl)
        if d is None:
            return []
        return list(d.keys())
    return None # wrong input.. return nothing

trainMarkovModel()

class MarkovKeyboardGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Next Word Prediction Using Markov Model (Keyboard)")
        self.geometry("800x400")
        
        self.sentence = tk.StringVar()
        self.suggestions = []
        self.suggestion_index = -1  # To track the current suggestion

        # Prediction area
        self.suggestion_label = ttk.Label(self, text="Suggestions: ", font=("Arial", 14))
        self.suggestion_label.grid(row=0, column=0, columnspan=10, pady=10)

        # Input field
        self.entry = ttk.Entry(self, textvariable=self.sentence, width=80)
        self.entry.grid(row=1, column=0, columnspan=10, padx=10, pady=10)
        
        # Create keyboard layout
        self.create_keyboard()

    def create_keyboard(self):
        """Create a simple virtual keyboard layout."""
        buttons = [
            'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
            'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
            'z', 'x', 'c', 'v', 'b', 'n', 'm', 'Backspace', 'Space', 'Tab'
        ]

        row_val = 2
        col_val = 0

        for button in buttons:
            if button == 'Space':
                space_btn = ttk.Button(self, text="Space", command=lambda b=button: self.on_click(' '))
                space_btn.grid(row=row_val, column=col_val, columnspan=5, sticky='nsew', padx=5, pady=5)
                col_val += 5
            elif button == 'Tab':
                tab_btn = ttk.Button(self, text="Tab", command=self.on_tab)
                tab_btn.grid(row=row_val, column=col_val, columnspan=2, sticky='nsew', padx=5, pady=5)
                col_val += 2
            elif button == 'Backspace':
                backspace_btn = ttk.Button(self, text="Backspace", command=self.on_backspace)
                backspace_btn.grid(row=row_val, column=col_val, sticky='nsew', padx=5, pady=5)
                col_val += 1
            else:
                btn = ttk.Button(self, text=button.upper(), command=lambda b=button: self.on_click(b))
                btn.grid(row=row_val, column=col_val, padx=5, pady=5, sticky='nsew')
                col_val += 1

            if col_val > 9:
                col_val = 0
                row_val += 1

    def on_click(self, char):
        """Insert character to the entry field when a button is clicked."""
        current_text = self.sentence.get()
        if char == ' ':
            self.sentence.set(current_text + ' ')
            self.predict_next_word()  # Predict the next word when space is clicked
        else:
            self.sentence.set(current_text + char)

    def on_backspace(self):
        """Remove the last character from the entry field."""
        current_text = self.sentence.get()
        self.sentence.set(current_text[:-1])  # Remove the last character

    def predict_next_word(self):
        """Triggered after pressing space, predicts the next word."""
        sentence = self.sentence.get().strip().lower()
        tokens = sentence.split()

        if len(tokens) == 1:
            self.suggestions = next_word(tokens[0])
        elif len(tokens) >= 2:
            self.suggestions = next_word((tokens[-2], tokens[-1]))

        self.suggestion_index = -1  # Reset the index each time we predict new words
        # Update the suggestion label with the available suggestions
        self.update_suggestions()

    def on_tab(self):
        """Cycle through the suggestions when Tab is pressed."""
        if self.suggestions:
            self.suggestion_index = (self.suggestion_index + 1) % len(self.suggestions)  # Cycle through suggestions
            selected_suggestion = self.suggestions[self.suggestion_index]
            sentence = self.sentence.get().strip()
            new_sentence = sentence + " " + selected_suggestion
            self.sentence.set(new_sentence)
            self.suggestions = []  # Clear suggestions after auto-completion
            self.update_suggestions()

    def update_suggestions(self):
        """Display the current suggestions."""
        if self.suggestions:
            self.suggestion_label.config(text="Suggestions: " + ", ".join(self.suggestions))
        else:
            self.suggestion_label.config(text="No suggestions available")

if __name__ == "__main__":
    app = MarkovKeyboardGUI()
    app.mainloop()
