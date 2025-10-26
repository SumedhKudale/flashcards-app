from django.contrib import admin
from .models import UserProfile, Deck, Card, ReviewSession

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cards_per_day', 'created_at']
    search_fields = ['user__username']
    list_filter = ['created_at']

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'get_total_cards']
    search_fields = ['name', 'user__username']
    list_filter = ['created_at', 'user']
    
    def get_total_cards(self, obj):
        return obj.get_total_cards()
    get_total_cards.short_description = 'Total Cards'

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['front_preview', 'deck', 'next_review_date', 'repetitions', 'ease_factor']
    search_fields = ['front', 'back', 'deck__name']
    list_filter = ['deck', 'next_review_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_reviewed']
    
    def front_preview(self, obj):
        return obj.front[:50]
    front_preview.short_description = 'Front'

@admin.register(ReviewSession)
class ReviewSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'deck', 'date', 'cards_reviewed', 'total_time']
    search_fields = ['user__username', 'deck__name']
    list_filter = ['date', 'user', 'deck']
