import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter


class BookMakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Maker")
        self.root.geometry("800x600")

        # Variables
        self.cover_image_path = None
        self.chapters = []  # Stores chapters as tuples (title, content)
        self.book_title = tk.StringVar(value="My Book")
        self.book_author = tk.StringVar(value="Author Name")

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        # Book Title and Author
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10, fill="x", padx=10)

        tk.Label(title_frame, text="Book Title:").grid(row=0, column=0, padx=5, sticky="w")
        tk.Entry(title_frame, textvariable=self.book_title, width=50).grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(title_frame, text="Author:").grid(row=1, column=0, padx=5, sticky="w")
        tk.Entry(title_frame, textvariable=self.book_author, width=50).grid(row=1, column=1, padx=5, sticky="w")

        # Cover Image
        self.cover_label = tk.Label(self.root, text="No Cover Image Selected", bg="gray", width=50, height=10)
        self.cover_label.pack(pady=10)

        self.upload_button = tk.Button(self.root, text="Upload Cover Image", command=self.upload_cover_image)
        self.upload_button.pack(pady=5)

        # Chapter Management
        self.chapter_frame = tk.Frame(self.root)
        self.chapter_frame.pack(pady=10, fill="x", padx=10)

        self.chapter_list = tk.Listbox(self.chapter_frame, height=6)
        self.chapter_list.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.chapter_frame, orient="vertical", command=self.chapter_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.chapter_list.config(yscrollcommand=scrollbar.set)

        # Chapter Entry
        self.chapter_title_label = tk.Label(self.root, text="Chapter Title:")
        self.chapter_title_label.pack()
        self.chapter_title_entry = tk.Entry(self.root, width=50)
        self.chapter_title_entry.pack()

        self.text_label = tk.Label(self.root, text="Chapter Content:")
        self.text_label.pack()

        self.text_area = tk.Text(self.root, wrap="word", height=10)
        self.text_area.pack(pady=10, padx=10, fill="both", expand=True)

        # Chapter Buttons
        self.add_chapter_button = tk.Button(self.root, text="Add Chapter", command=self.add_chapter)
        self.add_chapter_button.pack(pady=5)

        # Save Button
        self.generate_button = tk.Button(self.root, text="Generate PDF", command=self.generate_pdf)
        self.generate_button.pack(pady=20)

    def upload_cover_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.cover_image_path = file_path
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            img_tk = ImageTk.PhotoImage(img)
            self.cover_label.config(image=img_tk, text="")
            self.cover_label.image = img_tk

    def add_chapter(self):
        title = self.chapter_title_entry.get().strip()
        content = self.text_area.get("1.0", tk.END).strip()

        if not title or not content:
            messagebox.showerror("Error", "Chapter title and content cannot be empty.")
            return

        self.chapters.append((title, content))
        self.chapter_list.insert(tk.END, title)

        # Clear inputs
        self.chapter_title_entry.delete(0, tk.END)
        self.text_area.delete("1.0", tk.END)

    def generate_pdf(self):
        if not self.cover_image_path:
            messagebox.showerror("Error", "Please upload a cover image.")
            return

        if not self.chapters:
            messagebox.showerror("Error", "Please add at least one chapter.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not save_path:
            return

        temp_path = "temp_output.pdf"  # Temporary file for intermediate output

        try:
            # Step 1: Write PDF with TOC at the end
            pdf = canvas.Canvas(temp_path, pagesize=letter)
            width, height = letter
            page_number = 1

            # Add cover page with title and image
            pdf.setFont("Times-Bold", 24)
            pdf.drawCentredString(width / 2, height - 100, self.book_title.get())
            pdf.setFont("Times-Roman", 16)
            pdf.drawCentredString(width / 2, height - 130, f"by {self.book_author.get()}")
            if self.cover_image_path:
                pdf.drawImage(self.cover_image_path, 100, height - 450, width=width - 200, height=300)
            pdf.showPage()
            page_number += 1

            # Chapters and record start pages
            chapter_start_pages = {}
            for title, content in self.chapters:
                chapter_start_pages[title] = page_number
                pdf.setFont("Times-Bold", 18)
                pdf.drawCentredString(width / 2, height - 50, title)
                pdf.setFont("Times-Roman", 12)

                # Print chapter content
                text_object = pdf.beginText(50, height - 100)
                text_object.setFont("Times-Roman", 12)
                lines = content.split("\n")
                for line in lines:
                    if text_object.getY() < 50:
                        pdf.drawText(text_object)
                        pdf.drawRightString(width - 50, 30, f"Page {page_number}")
                        pdf.showPage()
                        page_number += 1
                        text_object = pdf.beginText(50, height - 50)
                        text_object.setFont("Times-Roman", 12)
                    text_object.textLine(line)
                pdf.drawText(text_object)
                pdf.drawRightString(width - 50, 30, f"Page {page_number}")
                pdf.showPage()
                page_number += 1

            # Write TOC at the end
            pdf.setFont("Times-Bold", 18)
            pdf.drawCentredString(width / 2, height - 50, "Table of Contents")
            pdf.setFont("Times-Roman", 12)
            toc_y = height - 100
            for title, start_page in chapter_start_pages.items():
                pdf.drawString(50, toc_y, f"{title} ........ Page {start_page}")
                toc_y -= 20
                if toc_y < 50:
                    pdf.showPage()
                    toc_y = height - 100

            pdf.save()

            # Step 2: Rearrange TOC to its proper place
            reader = PdfReader(temp_path)
            writer = PdfWriter()

            # Add cover page
            writer.add_page(reader.pages[0])

            # Add TOC
            writer.add_page(reader.pages[-1])

            # Add remaining pages (chapters)
            for i in range(1, len(reader.pages) - 1):
                writer.add_page(reader.pages[i])

            # Save final PDF
            with open(save_path, "wb") as output_file:
                writer.write(output_file)

            messagebox.showinfo("Success", f"PDF saved successfully at {save_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {e}")

    def clean_up_temp_file(self, temp_path):
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = BookMakerApp(root)
    root.mainloop()
