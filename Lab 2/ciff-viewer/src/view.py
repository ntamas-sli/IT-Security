from tkinter import Tk, Menu, messagebox, filedialog, Canvas, Frame, NW, Label
from ciff import CIFF
from PIL import Image, ImageTk


class Window(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        
        self.master = master
        self._setup_window()
        self.winfo_toplevel().title("CIF Viewer")
        
        self.current_image_id = None
        self.current_image = None

    def _setup_window(self):
        # menu bar
        menubar = Menu(root)

        # File menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_image)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)  # add File menu to the menu bar

        # Help menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=Window.help)
        menubar.add_cascade(label="Help", menu=helpmenu)  # add Help menu to the menu bar

        # add menu bar to the display
        self.master.config(menu=menubar)

        # canvas to display the image
        self.canvas = Canvas(self.master, width=800, height=600)
        self.canvas.grid(row=0, column=0)

        # frame to display info from header
        self.frame = Frame(self.master)
        self.frame.grid(row=0, column=1, sticky="n")

    @staticmethod
    def help():
        messagebox.showinfo("About...", "CIFF viewer\nversion 1.0")

    def open_image(self) -> None:
        file_path = filedialog.askopenfilename()
        # check if a file was selected
        if file_path != () and file_path != "":
            # parse the file
            try:
                ciff_image = CIFF.parse_ciff_file(file_path)
                if ciff_image.is_valid:
                    # only display valid CIFF images

                    # canvas to display the image
                    self.canvas.destroy()
                    self.canvas = Canvas(self.master, width=800, height=600)

                    # convert pixels into displayable image
                    pil_image = Image.new('RGB', (ciff_image.width, ciff_image.height))
                    pil_image.putdata(ciff_image.pixels)  # type: ignore  # generic function that return the correct type in this case
                    pil_image.thumbnail((800,600))  # resize image to fit canvas
                    photo_image = ImageTk.PhotoImage(image=pil_image)

                    # display image on canvas
                    self.canvas.create_image(0, 0, image=photo_image, anchor=NW)
                    self.canvas.grid(row=0, column=0)

                    # keep reference to image so that it is not garbage collected
                    self.current_image = photo_image

                    # frame display other info
                    self.frame.destroy()
                    self.frame = Frame(self.master)
                    self.frame.grid(row=0, column=1, sticky="n")

                    # display dimension of the image
                    dim = Label(self.frame, text="Dimensions:", wraplength=1000)
                    dim.grid(row=0, column=1)
                    dim_text = Label(self.frame, text="%s x %s" % (ciff_image.width, ciff_image.height), wraplength=1000)
                    dim_text.grid(row=0, column=2)

                    # display caption of the image
                    cap = Label(self.frame, text="Caption:")
                    cap.grid(row=1, column=1)
                    cap_text = Label(self.frame, text=ciff_image.caption, wraplength=1000)
                    cap_text.grid(row=1, column=2)

                    # display tags
                    tags = Label(self.frame, text="Tags:")
                    tags.grid(row=2, column=1)
                    for i in range(0, len(ciff_image.tags)):
                        t = Label(self.frame, text=ciff_image.tags[i][:-1], wraplength=1000)
                        t.grid(row=2+i, column=2)
                else:
                    messagebox.showerror("Error", "Invalid image!")
            except Exception as e:
                messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    # root window to display widgets in
    root = Tk()
    # set root window size
    root.geometry('1200x600')
    # create an instance
    app = Window(root)
    # run event loop
    root.mainloop()
