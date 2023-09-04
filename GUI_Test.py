from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"

class ChatClient:
    def __init__(self):
        self.clientWindow = Tk()
        self.setupWindow()
    
    def setupWindow(self):
        self.clientWindow.title("Chat Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=470, height=550, bg=bg_color)

        # Chat window
        self.chat_window = Text(self.clientWindow, width=20, height=2, bg=bg_color, fg=text_color, padx=4,pady=4)
        self.chat_window.place(relheight=0.675, relwidth=1, rely=0.1)
        self.chat_window.configure(state=DISABLED)

        # Scrollbar
        scrollbar = Scrollbar(self.chat_window)
        scrollbar.place(relheight=1, relx=0.967)
        scrollbar.configure(command=self.chat_window.yview)

        # Bottom label
        bottom_label = Label(self.clientWindow, bg=bg_bottom, height=80)
        bottom_label.place(relwidth=1, rely=0.8)
        
        # User input area
        self.user_input = Entry(bottom_label, bg=bg_entry, fg=text_color)
        self.user_input.place(relwidth=0.75, relheight=0.05, rely=0.01, relx=0.01)
        self.user_input.focus()
        self.user_input.bind("<Return>", self.pressedEnter)

        # Button for sending
        send_button = Button(bottom_label, text="Send", width=20, bg=bg_bottom, command=lambda: self.pressedEnter(None))
        send_button.place(relx=0.7, rely=0.01, relheight=0.05, relwidth=0.2)
    
    def run(self):
        self.clientWindow.mainloop()
    
    def pressedEnter(self, event):
        msg = self.user_input.get()
        self.sendMessage(msg, "You")

    def sendMessage(self, msg, sender):
        if not msg:
            return
        
        # Clear user input and use f string to format message
        self.user_input.delete(0, END)
        msg1 = f"{sender}: {msg}\n"

        self.chat_window.configure(state=NORMAL)
        self.chat_window.insert(END, msg1)
        self.chat_window.configure(state=DISABLED)

        self.chat_window.see(END)

if __name__ == '__main__':
    client = ChatClient()
    client.run()