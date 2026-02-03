from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from .models import AdminRegister
from django.http import JsonResponse


from django.contrib import messages
from  .models import Language, Genre, Movie, WebSeries,Season, Episode



def admin_register_page(request):
    if request.method == "POST":
        # Using the exact 'admin_' prefix you added to the HTML
         # 1. Capture the data from the HTML 'name' tags
        fname = request.POST.get('admin_first_name')
        lname = request.POST.get('admin_last_name')
        u_email = request.POST.get('admin_email')
        
        # ADD THIS LINE: This grabs what the user typed in the Username box
        u_username = request.POST.get('admin_username') 
        
        u_mobileno = request.POST.get('admin_mobileno')
        u_pwd = request.POST.get('admin_password')
        u_pic = request.FILES.get('admin_profile_pic')

        # 2. Save it to the Database
        new_admin = AdminRegister(
            admin_first_name=fname,
            admin_last_name=lname,
            admin_email=u_email,
            admin_username=u_username, # SAVE THE USERNAME HERE
            admin_mobileno=u_mobileno,
            admin_password=u_pwd,
            admin_profile_pic=u_pic
        )
        try:
           new_admin.save()
        except IntegrityError:
          # Handle the error, e.g., redirect back with a message
         print("Email already exists!")

        # After saving, send them to the login page
        return redirect('/admin_panel/admin_login_page/')
    
    return render(request, 'admin_panel/Internship28-octOR.html')


def admin_login_page(request):
    if request.method == "POST":
        username_entered = request.POST.get('admin_entered_username')
        password_entered = request.POST.get('admin_entered_password')

        try:
            admin = AdminRegister.objects.get(admin_username=username_entered, admin_password=password_entered)
            
            # Store the Admin's ID in the session
            request.session['admin_id'] = admin.id 
            
            return redirect('/admin_panel/admin_dashboard_page/') 
            
        except AdminRegister.DoesNotExist:
            return render(request, 'admin_panel/Internship28-octOL.html', {'error': 'Invalid Credentials'})

    return render(request, 'admin_panel/Internship28-octOL.html')

    
def admin_dashboard_page(request):
    # Fetching the admin data for the profile section
    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)

    # 1. Get the counts from your models
    movie_count = Movie.objects.count()
    language_count = Language.objects.count()
    genre_count = Genre.objects.count()
    series_count = WebSeries.objects.count()

    # 2. Add these counts to the context dictionary
    context = {
        'admin': admin,
        'movie_count': movie_count,
        'language_count': language_count,
        'genre_count': genre_count,
        'series_count': series_count,
    }
    return render(request, 'admin_panel/Internship4-octOD.html', context)

def admin_update_profile(request):
    if request.method == "POST":
        admin_id = request.session.get('admin_id')
        admin = AdminRegister.objects.get(id=admin_id)

        # Update text fields
        admin.admin_first_name = request.POST.get('admin_modal_first_name')
        admin.admin_last_name = request.POST.get('admin_modal_last_name')
        admin.admin_email = request.POST.get('admin_modal_email')
        
        # SAVE THE USERNAME HERE
        admin.admin_username = request.POST.get('admin_modal_username')

        # SAFELY UPDATE PROFILE PIC
        new_pic = request.FILES.get('admin_profile_pic')
        if new_pic: # Only updates if you actually chose a new file
            admin.admin_profile_pic = new_pic

        admin.save()
        return redirect('/admin_panel/admin_dashboard_page/')
    

# --

def admin_language_page(request):
    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)
    languages = Language.objects.all() # Fetch from DB
    
    return render(request, "admin_panel/Internship4-octOLang.html", {
        'admin': admin, 
        'languages': languages
    })

#  View to handle form submission
def add_language(request):
    if request.method == "POST":
        name = request.POST.get('admin_language_name')
        if name:
            Language.objects.create(language_name=name)
    return redirect('/admin_panel/admin_language_page/')

#  View to handle deletion
def delete_language(request, lang_id):
    Language.objects.get(id=lang_id).delete()
    return redirect('/admin_panel/admin_language_page/')

# Update language
def update_language(request, lang_id):
    if request.method == "POST":
        # Fetch the specific language object
        language = get_object_or_404(Language, id=lang_id)
        # Update the language name from the form input
        language.language_name = request.POST.get('language_name')
        language.save()
        return redirect('admin_language')
# --

def admin_genre_page(request):
    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)
    # Fetch all genres from the database
    genres = Genre.objects.all()
    
    return render(request, "admin_panel/Internship4-octOGenre.html", {
        'admin': admin,
        'genres': genres
    })

def add_genre(request):
    if request.method == "POST":
        cat = request.POST.get('admin_category')
        gen = request.POST.get('admin_genre_name')
        if cat and gen:
            Genre.objects.create(category_name=cat, genre_name=gen)
    return redirect('/admin_panel/admin_genre_page/')

def delete_genre(request, genre_id):
    Genre.objects.get(id=genre_id).delete()
    return redirect('/admin_panel/admin_genre_page/')

def update_genre(request, genre_id):
    if request.method == "POST":
        genre = get_object_or_404(Genre, id=genre_id)
        # Get the updated values from the modal form
        genre.category_name = request.POST.get('category_name')
        genre.genre_name = request.POST.get('genre_name')
        genre.save()
        return redirect('admin_genre_page')
# --

def admin_movie_page(request):
    # --- ADD THIS LOGIC TO FETCH ADMIN DATA ---
    admin_id = request.session.get('admin_id')
    admin_data = None
    if admin_id:
        admin_data = AdminRegister.objects.get(id=admin_id)
    else:
        return redirect('admin_login') # Security: send back to login if no session

    # --- YOUR EXISTING FILTER LOGIC ---
    selected_lang = request.GET.get('lang')
    selected_genre = request.GET.get('genre')
    movies = Movie.objects.all().order_by('-id')

    if selected_lang:
        movies = movies.filter(movie_language_id=selected_lang)
    if selected_genre:
        movies = movies.filter(movie_genre_id=selected_genre)

    languages = Language.objects.all()
    genres = Genre.objects.all()
    
    # --- UPDATE THE CONTEXT TO INCLUDE 'admin' ---
    return render(request, 'admin_panel/Internship11-decOM.html', {
        'movies': movies,
        'languages': languages,
        'genres': genres,
        'admin': admin_data  # Pass the admin object here
    })

def add_movie_action(request):
    if request.method == "POST":
        # Check if these IDs are actually coming through
        lang_id = request.POST.get('movie_language')
        gen_id = request.POST.get('movie_genre')

        # Create the object
        new_movie = Movie(
            movie_title=request.POST.get('movie_title'),
            movie_director=request.POST.get('movie_director'),
            movie_release_date=request.POST.get('movie_release_date'),
            movie_language_id=lang_id, # This matches the 'name' in HTML
            movie_genre_id=gen_id,      # This matches the 'name' in HTML
            movie_banner=request.FILES.get('movie_banner'),
            movie_duration=request.POST.get('movie_duration'),
            movie_description=request.POST.get('movie_description'),
            movie_video_url=request.POST.get('movie_video_url')
        )
        new_movie.save()
        return redirect('admin_movie_page')
    # Fetch data to display
    movies = Movie.objects.all()
    languages = Language.objects.all()
    genres = Genre.objects.all()
    
    return render(request, 'Internship11-decOM.html', {
        'movies': movies,
        'languages': languages,
        'genres': genres
    })

def delete_movie(request, movie_id):
    # Fetch the movie or return a 404 error if it doesn't exist
    movie = get_object_or_404(Movie, id=movie_id)
    movie.delete()
    return redirect('admin_movie_page')


def update_movie(request, movie_id):
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Updating all requested fields
        movie.movie_title = request.POST.get('movie_title')
        movie.movie_director = request.POST.get('movie_director')
        movie.movie_release_date = request.POST.get('movie_release_date')
        movie.movie_duration = request.POST.get('movie_duration')
        movie.movie_description = request.POST.get('movie_description')
        movie.movie_video_url = request.POST.get('movie_video_url')
        
        # Updating Foreign Keys for Language and Genre
        movie.movie_language_id = request.POST.get('movie_language')
        movie.movie_genre_id = request.POST.get('movie_genre')
        
        # Update banner only if a new file is uploaded
        if request.FILES.get('movie_banner'):
            movie.movie_banner = request.FILES.get('movie_banner')
            
        movie.save()
        return redirect('admin_movie_page')

# --


def admin_web_series_page(request):
    admin_id = request.session.get('admin_id')
    admin_data = AdminRegister.objects.get(id=admin_id)
    
    # 1. Get the filter values from the URL
    lang_id = request.GET.get('language')
    genre_id = request.GET.get('genre')

    # 2. Start with all webseries
    all_webseries = WebSeries.objects.all().order_by('-created_at')

    # 3. Apply filters using the CORRECT field names from your error message
    if lang_id:
        # Changed from web_series_language_id to series_language_id
        all_webseries = all_webseries.filter(series_language_id=lang_id)
    
    if genre_id:
        # Changed from web_series_genre_id to series_genre_id
        all_webseries = all_webseries.filter(series_genre_id=genre_id)

    # 4. Fetch languages and genres for dropdowns
    languages = Language.objects.all()
    genres = Genre.objects.all()
    
    return render(request, 'admin_panel/Internship23-decOW.html', {
        'all_webseries': all_webseries,
        'admin': admin_data,
        'languages': languages,
        'genres': genres,
        'selected_lang': lang_id,
        'selected_gen': genre_id
    })



def add_web_series_action(request):
    if request.method == "POST":
        WebSeries.objects.create(
            series_title=request.POST.get('series_title'),
            series_director=request.POST.get('series_director'),
            series_language_id=request.POST.get('series_language'),
            series_genre_id=request.POST.get('series_genre'),
            total_seasons=request.POST.get('total_seasons'),
            # UPDATE 
            release_date=request.POST.get('release_date'), 
            series_banner=request.FILES.get('series_banner')
        )
        return redirect('/admin_panel/admin_web_series_page/')
    

def delete_web_series_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        
        # This will delete the Series, and CASCADE will handle Seasons & Episodes
        series = get_object_or_404(WebSeries, id=series_id)
        series_name = series.series_title
        series.delete()
        
        messages.error(request, f"Successfully deleted the entire series: {series_name}")
    return redirect('/admin_panel/admin_web_series_page/')

def add_season_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        series = WebSeries.objects.get(id=series_id)
        
        # Increment the season count
        series.total_seasons += 1
        series.save()
        
        messages.success(request, f"Season {series.total_seasons} added to {series.series_title}!")
    return redirect('/admin_panel/admin_web_series_page/')




# views.py
def add_episode_action(request):
    if request.method == "POST":
        Episode.objects.create(
            series_id=request.POST.get('series_id'),
            season_id=request.POST.get('season_id'),
            episode_title=request.POST.get('ep_title'),
            video_url=request.POST.get('ep_url'),
            # ADD THESE
            episode_release_date=request.POST.get('ep_release_date'),
            episode_banner=request.FILES.get('ep_banner')
        )
        return redirect('/admin_panel/admin_web_series_page/')
    
def define_seasons_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        new_names = request.POST.getlist('season_names[]')
        release_dates = request.POST.getlist('season_release_dates[]')
        
        series = WebSeries.objects.get(id=series_id)
        current_seasons = series.seasons_list.all().order_by('season_order')
        
        for index, name in enumerate(new_names):
            order = index + 1
            rel_date = release_dates[index] if index < len(release_dates) else None
            
            # CHANGE: Fetch the specific file using the unique name we created in HTML
            banner = request.FILES.get(f'season_banner_{index}')

            if index < len(current_seasons):
                season = current_seasons[index]
                season.season_name = name
                if rel_date: 
                    season.season_release_date = rel_date
                if banner: 
                    season.season_banner = banner
                season.save()
            else:
                # Logic for creating new seasons if needed
                Season.objects.create(
                    series=series,
                    season_name=name,
                    season_order=order,
                    season_release_date=rel_date,
                    season_banner=banner
                )
        return redirect('/admin_panel/admin_web_series_page/')




def get_episodes_for_edit(request):
    series_id = request.GET.get('series_id')
    season_id = request.GET.get('season_id')
    episodes = Episode.objects.filter(series_id=series_id, season_id=season_id)
    
    episode_list = []
    for ep in episodes:
        episode_list.append({
            'id': ep.id,
            'title': ep.episode_title,
            'url': ep.video_url,
            # Ensure the date format is compatible with <input type="date">
            'release_date': ep.episode_release_date.strftime('%Y-%m-%d') if ep.episode_release_date else '',
            # This key MUST match your JavaScript 'ep.banner_url'
            'banner_url': ep.episode_banner.url if ep.episode_banner else None 
        })
    return JsonResponse({'episodes': episode_list})

def update_series_basic_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        series = get_object_or_404(WebSeries, id=series_id)
        
        # Update Text Fields
        series.series_title = request.POST.get('series_title')
        series.series_director = request.POST.get('series_director')
        
        # Update Foreign Keys (Language & Genre)
        series.series_language_id = request.POST.get('series_language')
        series.series_genre_id = request.POST.get('series_genre')
        
        # Update Banner if provided
        new_banner = request.FILES.get('series_banner')
        if new_banner:
            series.series_banner = new_banner
            
        series.save()
        messages.success(request, f"Series '{series.series_title}' updated successfully.")
        
    return redirect('/admin_panel/admin_web_series_page/')



def update_episode_action(request):
    if request.method == "POST":
        ep_id = request.POST.get('ep_id')
        try:
            episode = Episode.objects.get(id=ep_id)
            
            # Use the 'name' attributes from your JavaScript: ep_name, ep_url, ep_date
            episode.episode_title = request.POST.get('ep_name')
            episode.video_url = request.POST.get('ep_url')
            
            # Update Date
            new_date = request.POST.get('ep_date')
            if new_date:
                episode.episode_release_date = new_date
            
            # Update Banner File
            if request.FILES.get('ep_banner'):
                episode.episode_banner = request.FILES.get('ep_banner')
                
            episode.save()
            messages.success(request, "Episode updated successfully!")
        except Episode.DoesNotExist:
            messages.error(request, "Episode not found.")
            
    return redirect('/admin_panel/admin_web_series_page/')

# views.py

# views.py

def update_bulk_episodes_action(request):
    if request.method == "POST":
        # 1. Use .getlist() to capture all arrays from the form
        ep_ids = request.POST.getlist('ep_id[]')
        titles = request.POST.getlist('ep_title[]')
        urls = request.POST.getlist('ep_url[]')
        dates = request.POST.getlist('ep_release_date[]')

        # 2. Iterate through the IDs to update each episode record
        for i in range(len(ep_ids)):
            try:
                episode = Episode.objects.get(id=ep_ids[i])
                episode.episode_title = titles[i]
                episode.video_url = urls[i]
                
                # Check if a date was actually selected
                if i < len(dates) and dates[i]:
                    episode.episode_release_date = dates[i]

                # 3. Match the specific banner file to this episode index
                # Matches your JS: <input type="file" name="ep_banner_${index}">
                banner_field_name = f'ep_banner_{i}'
                if banner_field_name in request.FILES:
                    episode.episode_banner = request.FILES[banner_field_name]

                episode.save()
            except Episode.DoesNotExist:
                continue

        messages.success(request, "All episodes updated successfully!")
    
    return redirect('/admin_panel/admin_web_series_page/')


def delete_episode_action(request):
    if request.method == "POST":
        ep_id = request.POST.get('ep_id')
        Episode.objects.filter(id=ep_id).delete()
        messages.success(request, "Episode deleted successfully.")
    return redirect('/admin_panel/admin_web_series_page/')

def delete_season_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        # This is now receiving the Season ID from your hidden input
        season_id = request.POST.get('season_num') 
        
        # 1. Delete all episodes linked to this specific Season ID
        # Changed 'season_number' to 'season_id'
        Episode.objects.filter(series_id=series_id, season_id=season_id).delete()
        
        # 2. Optional: If you want to delete the Season name record too
        Season.objects.filter(id=season_id).delete()
        
        # 3. Sync the total_seasons count
        series = WebSeries.objects.get(id=series_id)
        if series.total_seasons > 0:
            series.total_seasons -= 1
            series.save()
            
        messages.success(request, f"Season deleted successfully.")
    return redirect('/admin_panel/admin_web_series_page/')

# views.py


def admin_profile_settings_page(request):

    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)
    return render(request, 'admin_panel/Internship5-decOP.html', {
        'admin': admin  # Pass the admin object here
    })

