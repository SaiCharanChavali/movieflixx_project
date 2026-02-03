from django.db import models


class AdminRegister(models.Model):
    admin_first_name = models.CharField(max_length=100)
    admin_last_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_mobileno = models.CharField(max_length=15)
    admin_password = models.CharField(max_length=128) # Use hashing in production
    admin_profile_pic = models.ImageField(upload_to='admin_profiles/', null=True, blank=True)
    admin_username = models.CharField(max_length=100, null=True, blank=True)



# Create your models here.
class Language(models.Model):
    # This stores the name of the language (e.g., "English", "Hindi")
    language_name = models.CharField(max_length=100, unique=True)  # <-- enforce uniqueness
    # Automatically adds the date when the language was entered
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.language_name
class Genre(models.Model):
    category_name = models.CharField(max_length=100)
    genre_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('category_name', 'genre_name')  # <-- enforce unique per category

    def _str_(self):
        return f"{self.category_name} - {self.genre_name}"    



from django.db import models

class Movie(models.Model):
    movie_title = models.CharField(max_length=255)
    movie_director = models.CharField(max_length=255)
    movie_release_date = models.DateField()

    movie_language = models.ForeignKey('Language', on_delete=models.CASCADE)
    movie_genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    movie_banner = models.ImageField(upload_to='movie_banners/')
    movie_duration = models.CharField(max_length=50)
    movie_description = models.TextField()
    movie_video_url = models.URLField()

    @property
    def get_embed_url(self):
        url = self.movie_video_url
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return url

    def __str__(self):
        return self.movie_title








from django.db import models

# ... (Language, Genre, Movie models stay the same) ...

class WebSeries(models.Model):
    series_title = models.CharField(max_length=255)
    series_director = models.CharField(max_length=255, default="Unknown")
    series_language = models.ForeignKey('Language', on_delete=models.CASCADE, null=True)
    series_genre = models.ForeignKey('Genre', on_delete=models.CASCADE, null=True)
    series_banner = models.ImageField(upload_to='webseries_banners/')
    total_seasons = models.IntegerField(default=1)
    release_date = models.DateField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    # FIX: Update this to use the Season relationship
    def get_episodes_count(self):
        counts = []
        # Loop through the seasons defined for this series
        for sn in self.seasons_list.all().order_by('season_order'):
            count = Episode.objects.filter(season=sn).count()
            counts.append(f"{sn.season_name}: {count} Episodes")
        return counts
    
    def total_seasons_range(self):
        return range(1, self.total_seasons + 1)



class Season(models.Model):
    series = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='seasons_list')
    season_name = models.CharField(max_length=100)
    season_order = models.IntegerField()
    # ADD THESE TWO FIELDS
    season_release_date = models.DateField(null=True, blank=True)
    season_banner = models.ImageField(upload_to='season_banners/', null=True, blank=True)

class Episode(models.Model):
    series = models.ForeignKey(WebSeries, on_delete=models.CASCADE, related_name='episodes')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_episodes', null=True)
    episode_title = models.CharField(max_length=255)
    video_url = models.URLField()
    # ADD THESE TWO FIELDS
    episode_release_date = models.DateField(null=True, blank=True)
    episode_banner = models.ImageField(upload_to='episode_banners/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    @property
    def get_embed_url(self):
        url = self.video_url
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return url
    
    