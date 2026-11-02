from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify

from .forms import CheckoutForm, RegistrationForm
from .models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    QuizQuestion,
    ShortAnswerQuestion,
)


class LearningAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus', None)


class LearningRegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus', None)


def learning_page(request, page):
    questions = list(QuizQuestion.objects.all())
    short_questions = list(ShortAnswerQuestion.objects.all())
    quiz_result = None
    quiz_error = None
    quiz_mode = 'multiple-choice'
    for question in questions:
        question.selected_answer = None
        question.selected_answer_text = ''
        question.is_correct = None
    for question in short_questions:
        question.submitted_answer = ''
        question.is_correct = None

    if request.method == 'POST':
        quiz_mode = request.POST.get('quiz_type', 'multiple-choice')
        active_questions = (
            short_questions if quiz_mode == 'short-answer' else questions
        )
        if quiz_mode not in ('multiple-choice', 'short-answer'):
            quiz_error = 'Choose a quiz format and try again.'
        elif not active_questions:
            quiz_error = 'The quiz is not available yet. Please try again later.'
        else:
            answers = []
            for question in active_questions:
                field_name = f'question_{question.pk}'
                submitted = request.POST.get(field_name, '')
                if quiz_mode == 'short-answer':
                    question.submitted_answer = submitted.strip()
                    if not question.submitted_answer:
                        quiz_error = 'Please answer every question.'
                        break
                    accepted_answers = {
                        answer.strip().casefold()
                        for answer in question.accepted_answers
                    }
                    is_correct = (
                        question.submitted_answer.casefold() in accepted_answers
                    )
                    question.is_correct = is_correct
                    answers.append((question, is_correct))
                else:
                    if (
                        not submitted.isdecimal()
                        or int(submitted) >= len(question.options)
                    ):
                        quiz_error = 'Please choose an answer for every question.'
                        break
                    question.selected_answer = int(submitted)
                    question.selected_answer_text = question.options[
                        question.selected_answer
                    ]
                    answers.append((
                        question,
                        question.selected_answer == question.correct_option,
                    ))

            if not quiz_error:
                score = sum(is_correct for _, is_correct in answers)
                quiz_result = {
                    'score': score,
                    'total': len(active_questions),
                    'percent': round(score * 100 / len(active_questions)),
                }
                if quiz_mode == 'multiple-choice':
                    for question, _ in answers:
                        question.is_correct = (
                            question.selected_answer == question.correct_option
                        )

    return render(request, 'home.html', {
        'page': page,
        'questions': questions,
        'short_questions': short_questions,
        'quiz_result': quiz_result,
        'quiz_error': quiz_error,
        'quiz_mode': quiz_mode,
    })


def home(request):
    return learning_page(request, 'home')


def relation(request):
    return learning_page(request, 'relation')


def questions(request):
    return learning_page(request, 'questions')


class LearningLoginView(auth_views.LoginView):
    template_name = 'account.html'
    authentication_form = LearningAuthenticationForm
    extra_context = {'account_mode': 'login'}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.get_redirect_url() or reverse('home')


def learning_signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LearningRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your account has been created.')
        return redirect('home')
    return render(request, 'account.html', {
        'account_mode': 'signup',
        'form': form,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True, stock__gt=0).select_related('category')
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search_query:
        products = products.filter(name__icontains=search_query)

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'active_category': category_slug,
        'search_query': search_query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product', 'product__category')
    total = sum((item.line_total for item in items), Decimal('0.00'))
    return render(request, 'shop/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('shop:product_list')

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1},
    )
    if not created:
        item.quantity += 1

    if item.quantity > product.stock:
        if created:
            item.delete()
        messages.error(request, 'There is not enough stock for that quantity.')
    else:
        item.save()
        messages.success(request, f'{product.name} added to your cart.')

    return redirect('shop:cart')


@login_required
def update_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('shop:cart')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    try:
        quantity = int(request.POST.get('quantity', ''))
    except (TypeError, ValueError):
        quantity = 0

    if quantity < 1:
        messages.error(request, 'Enter a quantity of at least 1.')
    elif quantity > item.product.stock:
        messages.error(request, 'There is not enough stock for that quantity.')
    else:
        item.quantity = quantity
        item.save(update_fields=['quantity'])
        messages.success(request, 'Cart updated.')

    return redirect('shop:cart')


@login_required
def remove_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('shop:cart')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    get_object_or_404(CartItem, pk=item_id, cart=cart).delete()
    messages.success(request, 'Item removed from your cart.')
    return redirect('shop:cart')


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('shop:cart')

    form = CheckoutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                cart_items = list(
                    cart.items.select_related('product').select_for_update()
                )
                if not cart_items:
                    messages.info(request, 'Your cart is empty.')
                    return redirect('shop:cart')

                total = Decimal('0.00')
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item.product_id)
                    if not product.is_active or item.quantity > product.stock:
                        raise ValueError(
                            f'{product.name} is no longer available in the requested quantity.'
                        )
                    total += product.price * item.quantity

                order = Order.objects.create(
                    user=request.user,
                    total=total,
                    **form.cleaned_data,
                )
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item.product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=item.quantity,
                    )
                    product.stock -= item.quantity
                    product.save(update_fields=['stock'])

                cart.items.all().delete()
        except ValueError as error:
            form.add_error(None, str(error))
        else:
            messages.success(request, 'Your order has been placed.')
            return redirect('shop:order_detail', order_id=order.pk)

    return render(request, 'shop/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_list(request):
    orders = request.user.orders.all()
    return render(request, 'shop/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        pk=order_id,
        user=request.user,
    )
    return render(request, 'shop/order_detail.html', {'order': order})


def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your account has been created.')
        return redirect('shop:product_list')
    return render(request, 'shop/register.html', {'form': form})


def success_page(request):
    return HttpResponse("hey this is a success page")
