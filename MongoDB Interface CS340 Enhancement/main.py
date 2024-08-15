import sys
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from pymongo import MongoClient
from bson import ObjectId
import subprocess

class MovieInterface:
    
    def __init__(self, master):
        self.master = master
        self.master.title("Movie Search Engine")

        # Connect to our MongoDB database
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['movie_list']
        self.movie_collection = self.db['movies']

        self.initWindow(self.master)
        self.initUI()
        self.initWidgets()
        
    # Setup the UI    
    def initUI(self):
        self.style = ttk.Style()
        self.style.configure('TLabel', background='mediumpurple4', foreground='black')
        self.style.configure('TFrame', background='mediumpurple4')
    
    # Set window parameters
    def initWindow(self, window):
        # Get user screen size
        screen_height = window.winfo_screenheight()
        screen_width = window.winfo_screenwidth()

        # Set desired application size
        window_height = 825
        window_width = 875

        # Use math to center on screen
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Set window geometry
        window.geometry(f'{window_width}x{window_height}+{x}+{y}')

    
    # Initialize our widgets for display
    def initWidgets(self):
        # Create the frame for searching
        self.search_frame = ttk.Frame(self.master, name="search_frame")
        self.search_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.search_frame.grid_propagate(False)
        self.search_frame.config(width=850, height=200)

        # Search bars and labels
        # Movie Search
        self.search_label = ttk.Label(self.search_frame, text="Movie Name:")
        self.search_label.grid(row=0, column=0, padx=10, pady=10)
        self.search_var = tk.StringVar()
        self.search_query = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_query.grid(row=0, column=1, padx=10, pady=10)

        # Actor Search
        self.actor_label = ttk.Label(self.search_frame, text="Actor:")
        self.actor_label.grid(row=1, column=0, padx=10, pady=10)
        self.actor_var = tk.StringVar()
        self.actor_query = ttk.Entry(self.search_frame, textvariable=self.actor_var)
        self.actor_query.grid(row=1, column=1, padx=10, pady=10)

        # Director Search
        self.director_label = ttk.Label(self.search_frame, text="Director:")
        self.director_label.grid(row=2, column=0, padx=10, pady=10)
        self.director_var = tk.StringVar()
        self.director_query = ttk.Entry(self.search_frame, textvariable=self.director_var)
        self.director_query.grid(row=2, column=1, padx=10, pady=10)

        # Sorting frame with radio buttons
        self.sort_order_frame = ttk.Frame(self.search_frame, name="sort_order_frame")
        self.sort_order_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.E)

        self.sort_var = tk.StringVar()
        self.sort_var.set("by movie name") # Default

        self.movie_name_radio = ttk.Radiobutton(self.sort_order_frame, text="By Movie Name", variable=self.sort_var, value="by movie name")
        self.movie_name_radio.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.year_radio = ttk.Radiobutton(self.sort_order_frame, text="By Year", variable=self.sort_var, value="by year")
        self.year_radio.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Create search and clear button
        self.buttons_frame = ttk.Frame(self.search_frame)
        self.buttons_frame.grid(row=1, column=3, columnspan=2, padx=200, pady=10, sticky=tk.E)

        self.search_button = ttk.Button(self.buttons_frame, text="Search", command=self.searchMovies)
        self.search_button.grid(row=0, column=0, padx=10, pady=10)

        self.clear_button = ttk.Button(self.buttons_frame, text="Clear", command=self.clearSearch)
        self.clear_button.grid(row=0, column=1, padx=10, pady=10)

        # Create tree view
        self.tree_view = ttk.Treeview(self.master, columns=("Title", "IMDb Rating", "Tomatoe's Rating", "Directors"), selectmode="browse")
        self.tree_view.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.tree_view.heading("#0", text="Year")
        self.tree_view.heading("Title", text="Title")
        self.tree_view.heading("IMDb Rating", text="IMDb Rating")
        self.tree_view.heading("Tomatoe's Rating", text="Tomatoe's Rating")
        self.tree_view.heading("Directors", text="Directors")

        # Change Width of Headings
        self.tree_view.column("#0", width=80)
        self.tree_view.column("Title", width=290)
        self.tree_view.column("IMDb Rating", width=80)
        self.tree_view.column("Tomatoe's Rating", width=105)
        self.tree_view.column("Directors", width=300)

        # Mouse click listeners
        # Double click will view movie poster
        self.tree_view.bind("<Double-1>", self.showPoster)

        # Description/Poster Display Frame
        self.description_frame = ttk.Frame(self.master, name="description_frame")
        self.description_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        self.description_frame.config(width=850, height=325)
        self.description_frame.grid_propagate(False)

        self.description_text = tk.Text(self.description_frame, wrap="word", height=19, width=80)
        self.description_text.config(state="disabled")
        self.description_text.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="w")

        self.poster_label = ttk.Label(self.description_frame, image=None)
        self.poster_label.image = None
        self.poster_label.grid(row=0, column=4, columnspan=4, padx=10, pady=10)
    
    def searchMovies(self):
        # Clear the Treeview
        self.tree_view.delete(*self.tree_view.get_children())

        # Clear the poster image
        self.poster_label.configure(image=None)

        # Prepare the search queries
        title_query = {"title": {"$regex": self.search_var.get(), "$options": "i"}}
        actor_query = {"cast": {"$regex": self.actor_var.get(), "$options": "i"}}
        director_query = {"directors": {"$regex": self.director_var.get(), "$options": "i"}}

        # Combine all queries with an AND operator
        query = {}
        if self.search_var.get():
            query.update(title_query)
        if self.actor_var.get():
            query.update(actor_query)
        if self.director_var.get():
            query.update(director_query)

        # Perform the search query if at least one condition is specified
        if query:
            # Add sorting based on sort_var
            sort_criteria = [("title", 1)]  # Default sorting by title
            if self.sort_var.get() == "by year":
                sort_criteria = [("year", 1)]

            # Projection to include additional fields
            projection = {"_id": 1, "title": 1, "year": 1, "genres": 1, "poster": 1, "imdb.rating": 1, "tomatoes.viewer.rating": 1, "directors": 1}

            movies = self.movie_collection.find(query, projection).sort(sort_criteria)

            # Populate the Treeview with the search results
            for movie in movies:
                movie_id = movie.get("_id")
                year = movie.get("year", "")
                imdb_rating = movie.get("imdb", {}).get("rating", "")
                tomatoes_rating = movie.get("tomatoes", {}).get("viewer", {}).get("rating", "")
                directors = ", ".join(movie.get("directors", []))

                self.tree_view.insert("", "end", text=year, values=(movie["title"], imdb_rating, tomatoes_rating, directors, movie_id))

        else:
            # Show a message if no search criteria are provided
            messagebox.showinfo("Info", "Please provide at least one search parameter")
    
    # Clear the search bars and empty the tree view
    def clearSearch(self):
        self.tree_view.delete(*self.tree_view.get_children())
        self.clearMovieDetails()
        self.search_var.set("")
        self.actor_var.set("")
        self.director_var.set("")

    # Empty our description/poster section
    def clearMovieDetails(self):
        try:
            if hasattr(self, 'description_frame') and isinstance(self.description_frame, (tk.Frame, ttk.Frame)):
                self.description_text.config(state="normal")
                self.description_text.delete("1.0", "end")
                self.description_text.config(state="disabled")
                self.poster_label.configure(image=None)
                self.poster_label.image = None
        except AttributeError:
            pass

    def showPoster(self, event):
        # Clear previous details
        self.clearMovieDetails()

        item = self.tree_view.selection()[0]
        values = self.tree_view.item(item, "values")
        movie_id = values[-1]
        movie = self.movie_collection.find_one({"_id": ObjectId(movie_id)})

        if movie:
            # Display description
            description = movie.get("fullplot", "")
            self.description_text.config(state="normal")
            self.description_text.delete("1.0", "end")
            self.description_text.insert("1.0", description)
            self.description_text.config(state="disabled")

            # Attempt to display movie poster
            if movie.get("poster", ""):
                response = requests.get(movie["poster"])
                if response.status_code == 200: # successful response
                    img = Image.open(BytesIO(response.content))
                    img.thumbnail((200, 200))
                    photo = ImageTk.PhotoImage(img)
                    self.poster_label.config(image=photo)
                    self.poster_label.image = photo

                    # Check for which platform the user is running
                    if sys.platform == "win32":
                        self.poster_label.bind("<Double-1>", lambda event: subprocess.Popen(["start", movie["poster"]], shell=True, start_new_session=True))
                    if sys.platform == "darwin":
                        self.poster_label.bind("<Double-1>", lambda event: subprocess.Popen(["open", movie["poster"]], shell=False, start_new_session=True))
                else:
                    messagebox.showerror("Error", "Failed to load poster URL.")
            else:
                messagebox.showerror("Info", "No poster available for this movie.")
        else:
            messagebox.showerror("Error", "Movie was not found.")

def main():

    root = tk.Tk()
    app = MovieInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()