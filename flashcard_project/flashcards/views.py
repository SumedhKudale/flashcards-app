from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import Deck, Card, UserProfile, ReviewSession
from .forms import RegisterForm, DeckForm, CardForm, UserProfileForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {username}!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')

@login_required
def home_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    decks = Deck.objects.filter(user=request.user).annotate(card_count=Count('cards'))
    
    total_decks = decks.count()
    total_cards = sum(deck.card_count for deck in decks)
    
    today = timezone.now().date()
    cards_due_today = Card.objects.filter(
        deck__user=request.user,
        next_review_date__lte=today
    ).count()
    
    context = {
        'decks': decks,
        'total_decks': total_decks,
        'total_cards': total_cards,
        'cards_due_today': cards_due_today,
        'user_profile': user_profile,
    }
    return render(request, 'home.html', context)

@login_required
def deck_list_view(request):
    decks = Deck.objects.filter(user=request.user).annotate(card_count=Count('cards'))
    return render(request, 'deck_list.html', {'decks': decks})

@login_required
def deck_create_view(request):
    if request.method == 'POST':
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.user = request.user
            deck.save()
            messages.success(request, 'Deck created successfully!')
            return redirect('deck_detail', deck_id=deck.id)
    else:
        form = DeckForm()
    
    return render(request, 'deck_form.html', {'form': form, 'title': 'Create New Deck'})

@login_required
def deck_detail_view(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    cards = deck.cards.all()
    user_profile = UserProfile.objects.get(user=request.user)
    
    today = timezone.now().date()
    cards_due = deck.cards.filter(next_review_date__lte=today).count()
    
    context = {
        'deck': deck,
        'cards': cards,
        'total_cards': cards.count(),
        'cards_due': cards_due,
    }
    return render(request, 'deck_detail.html', context)

@login_required
def deck_edit_view(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    
    if request.method == 'POST':
        form = DeckForm(request.POST, instance=deck)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deck updated successfully!')
            return redirect('deck_detail', deck_id=deck.id)
    else:
        form = DeckForm(instance=deck)
    
    return render(request, 'deck_form.html', {'form': form, 'title': 'Edit Deck', 'deck': deck})

@login_required
def deck_delete_view(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    
    if request.method == 'POST':
        deck_name = deck.name
        deck.delete()
        messages.success(request, f'Deck "{deck_name}" deleted successfully!')
        return redirect('deck_list')
    
    return render(request, 'deck_confirm_delete.html', {'deck': deck})

@login_required
def card_create_view(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.deck = deck
            card.save()
            messages.success(request, 'Card created successfully!')
            
            if 'save_and_add' in request.POST:
                return redirect('card_create', deck_id=deck.id)
            else:
                return redirect('deck_detail', deck_id=deck.id)
    else:
        form = CardForm()
    
    return render(request, 'card_form.html', {'form': form, 'deck': deck, 'title': 'Create New Card'})

@login_required
def card_edit_view(request, card_id):
    card = get_object_or_404(Card, id=card_id, deck__user=request.user)
    
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, 'Card updated successfully!')
            return redirect('deck_detail', deck_id=card.deck.id)
    else:
        form = CardForm(instance=card)
    
    return render(request, 'card_form.html', {'form': form, 'card': card, 'deck': card.deck, 'title': 'Edit Card'})

@login_required
def card_delete_view(request, card_id):
    card = get_object_or_404(Card, id=card_id, deck__user=request.user)
    deck_id = card.deck.id
    
    if request.method == 'POST':
        card.delete()
        messages.success(request, 'Card deleted successfully!')
        return redirect('deck_detail', deck_id=deck_id)
    
    return render(request, 'card_confirm_delete.html', {'card': card})

@login_required
def review_view(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    user_profile = UserProfile.objects.get(user=request.user)
    
    today = timezone.now().date()
    cards_due = deck.cards.filter(next_review_date__lte=today)[:user_profile.cards_per_day]
    
    if not cards_due:
        messages.info(request, 'No cards due for review today!')
        return redirect('deck_detail', deck_id=deck.id)
    
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        quality = int(request.POST.get('quality'))
        card = get_object_or_404(Card, id=card_id, deck=deck)
        
        card.update_sm2(quality)
        
        session, created = ReviewSession.objects.get_or_create(
            user=request.user,
            deck=deck,
            date=today
        )
        session.cards_reviewed += 1
        session.save()
        
        messages.success(request, 'Card reviewed!')
        return redirect('review', deck_id=deck.id)
    
    current_card = cards_due.first()
    remaining_cards = cards_due.count()
    
    context = {
        'deck': deck,
        'card': current_card,
        'remaining_cards': remaining_cards,
    }
    return render(request, 'review.html', context)

@login_required
def settings_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('home')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'settings.html', {'form': form, 'user_profile': user_profile})
