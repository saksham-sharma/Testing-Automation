import tkinter
import data_process
import continuous_spectrum
import time


def service_func():
    top = tkinter.Tk()
    top.geometry("1000x500")            # Sets the window size

    t = tkinter.Text(width=90, height=23)       # Creates the status window with width and height parameters

    def analyse():
        t.insert("4.0", "\nAnalyzing Data.....\n")
        top.update_idletasks()
        time.sleep(3)                           # Paused for dramatic effect, can be removed for instant results
        flag, amp_val, chplan = data_process.some_func()                 # Input variables for printing in status window
        if flag == 0:
            t.insert("5.0", "Mandatory channels not implemented\n")
            top.update_idletasks()
        else:
            t.insert("5.0", "The implemented channels are: ")
            t.insert("6.0", "{}\n".format(chplan))
            top.update_idletasks()
        # checking minimum power requirements
        try:
            if max(amp_val < 30):
                t.insert("7.0", "\nPower transmitted well within acceptable values\n")
                top.update_idletasks()
        except ValueError:
            t.insert("7.0", "No peak observed!")

    def read():
        t.insert("1.0", "Reading Data Values.....\n")
        top.update_idletasks()
        noise = continuous_spectrum.main()
        t.insert("2.0", "Noise Floor is: ")
        t.insert("3.0", "{} dB".format(noise))
        top.update_idletasks()

    def clear():
        t.delete('1.0', tkinter.END)

    h = tkinter.Label(text="DEVICE TESTING PROGRAM", font='Helvetica 18 bold')               # Creates the heading

    # Creating buttons for the window
    b2 = tkinter.Button(text="Start Reading Data", height='2', font='Helvetica 11', command=read)
    b2.place(x=20, y=80)

    b3 = tkinter.Button(text="Analyze Values", height='2', font='Helvetica 11', command=analyse)
    b3.place(x=20, y=160)

    b4 = tkinter.Button(text="Clear Status Window", height='2', font='Helvetica 11', command=clear)
    b4.place(x=20, y=240)

    b5 = tkinter.Button(text="Quit", height='2', font='Helvetica 11', command=exit)
    b5.place(x=20, y=320)

    t.place(x=240, y=80)

    h.pack()
    top.mainloop()


if __name__ == '__main__':
    service_func()
