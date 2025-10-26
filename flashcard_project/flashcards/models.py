from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cards_per_day = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_total_cards(self):
        return self.cards.count()
    
    def get_cards_due_today(self, user_profile):
        today = timezone.now().date()
        return self.cards.filter(next_review_date__lte=today).count()

class Card(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Again'),
        (2, 'Hard'),
        (3, 'Good'),
        (4, 'Easy'),
    ]
    
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    front = models.TextField()
    back = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Spaced repetition fields
    ease_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)  # Days until next review
    repetitions = models.IntegerField(default=0)
    next_review_date = models.DateField(default=timezone.now)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['next_review_date', '-created_at']
    
    def __str__(self):
        return f"{self.front[:50]}..."
    
    def update_sm2(self, quality):
        """
        SuperMemo 2 (SM-2) 
        """
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            
            self.repetitions += 1
        
        # Update ease factor
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Set next review date
        self.next_review_date = timezone.now().date() + timezone.timedelta(days=self.interval)
        self.last_reviewed = timezone.now()
        self.save()

class ReviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_sessions')
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='review_sessions')
    date = models.DateField(auto_now_add=True)
    cards_reviewed = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0)  # In seconds
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.deck.name} - {self.date}"
