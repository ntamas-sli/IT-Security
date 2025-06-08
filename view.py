from tkinter import Tk, Canvas, NW, Toplevel, Text, Scrollbar, VERTICAL, filedialog, messagebox, END
from tkinter.ttk import Frame, Label, Button
from ciff import CIFF
from os import listdir
from os.path import join, extsep
from PIL import Image, ImageTk


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self._setup_window()
        self.current_image = None
        self.show_landing_page()

    def _setup_window(self):
        # Buttons for actions
        button_frame = Frame(self.master)
        button_frame.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        Button(button_frame, text="Open Image", command=self.open_image).grid(row=0, column=0, padx=5)
        Button(button_frame, text="Run Tests", command=self.run_tests).grid(row=0, column=1, padx=5)
        Button(button_frame, text="About", command=self.show_help).grid(row=0, column=2, padx=5)

        # Canvas for images or landing page
        self.canvas = Canvas(self.master, width=800, height=600, bg="lightgray")
        self.canvas.grid(row=1, column=0, padx=10, pady=10)

        # Frame for metadata display
        self.info_frame = Frame(self.master)
        self.info_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

    def show_landing_page(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            400, 300,
            text="Welcome to CIFF Viewer\n\nOpen an image to start!",
            font=("Arial", 20, "bold"),
            fill="darkgray",
            justify="center"
        )

        # Default info panel content
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        Label(self.info_frame, text="Instructions:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        Label(self.info_frame, text="1. Click 'Open Image' to load a CIFF file.\n"
                                    "2. Use 'Run Tests' to validate all test images.\n"
                                    "3. Click 'About' for application info.",
              justify="left", wraplength=250).grid(row=1, column=0, sticky="w")

    def show_help(self):
        messagebox.showinfo("About", "CIFF Viewer\nVersion 1.0\nSimple image viewer for CIFF files.")

    def open_image(self):
        file_path = filedialog.askopenfilename(title="Select a CIFF Image", filetypes=[("CIFF Files", "*.ciff")])
        if not file_path:
            return

        try:
            ciff_image = CIFF.parse_ciff_file(file_path)
            if not ciff_image.is_valid:
                raise ValueError("Invalid CIFF image!")

            self.display_image(ciff_image)
            self.display_info(ciff_image)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def display_image(self, ciff_image):
        self.canvas.delete("all")

        pil_image = Image.new("RGB", (ciff_image.width, ciff_image.height))
        pil_image.putdata(ciff_image.pixels)
        photo_image = ImageTk.PhotoImage(pil_image, master=self.canvas)

        self.canvas.create_image(0, 0, image=photo_image, anchor=NW)
        self.current_image = photo_image

    def display_info(self, ciff_image):
        # Clear previous info
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        Label(self.info_frame, text="Image Information", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        Label(self.info_frame, text="Dimensions:").grid(row=1, column=0, sticky="w", pady=2)
        Label(self.info_frame, text=f"{ciff_image.width} x {ciff_image.height}").grid(row=1, column=1, sticky="w", pady=2)

        Label(self.info_frame, text="Caption:").grid(row=2, column=0, sticky="w", pady=2)
        Label(self.info_frame, text=ciff_image.caption, wraplength=250, justify="left").grid(row=2, column=1, sticky="w", pady=2)

        Label(self.info_frame, text="Tags:").grid(row=3, column=0, sticky="nw", pady=2)

        # Handling long tags
        max_tag_length = 50
        for i, tag in enumerate(ciff_image.tags):
            truncated_tag = (tag[:max_tag_length] + "...") if len(tag) > max_tag_length else tag
            Label(self.info_frame, text=truncated_tag, wraplength=250, justify="left").grid(row=3 + i, column=1, sticky="w", pady=2)

    def run_tests(self):
        test_window = Toplevel(self.master)
        test_window.title("CIFF Test Results")
        test_window.geometry("600x400")

        scrollbar = Scrollbar(test_window, orient=VERTICAL)
        result_text = Text(test_window, wrap="none", yscrollcommand=scrollbar.set)
        scrollbar.config(command=result_text.yview)
        scrollbar.pack(side="right", fill="y")
        result_text.pack(side="left", fill="both", expand=True)

        test_vectors_path = "test-vectors"
        try:
            for test_vector in sorted(
                [f for f in listdir(test_vectors_path)],
                key=lambda f: int(f.replace("test", "").rsplit(extsep, 1)[0].rsplit(None, 1)[-1])
            ):
                try:
                    ciff_file = CIFF.parse_ciff_file(join(test_vectors_path, test_vector))
                    if ciff_file.is_valid:
                        result_text.insert(END, f"{test_vector} is detected as VALID\n")
                    else:
                        result_text.insert(END, f"{test_vector} is detected as INVALID\n")
                except Exception as e:
                    result_text.insert(END, f"Error processing {test_vector}: {e}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run tests:\n{e}")


if __name__ == "__main__":
    root = Tk()  # Create the main Tkinter window
    root.title("CIFF Viewer")  # Set the window title
    root.geometry("1200x700")  # Set the default size of the window
    root.resizable(True, True)  # Allow the window to be resizable

    app = Window(root)  # Create an instance of the `Window` class
    root.mainloop()  # Start the Tkinter event loop
