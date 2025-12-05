from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Book


def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Получаем количество объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()

    # Количество книг, содержащих слово
    search_word = "war"  # вы можете изменить это слово
    num_books_with_word = Book.objects.filter(title__icontains=search_word).count()

    # Счётчик посещений
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'catalog/index.html',
        context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_genres': num_genres,
            'num_books_with_word': num_books_with_word,
            'search_word': search_word,
            'num_visits': num_visits,  # num_visits appended
        },
    )

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
        """
        Generic class-based view listing books on loan to current user.
        """
        model = BookInstance
        template_name = 'catalog/bookinstance_list_borrowed_user.html'
        paginate_by = 10

        def get_queryset(self):
            return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by(
                'due_back')




class BookListView(generic.ListView):
    model = Book
    paginate_by = 2

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 3

class AuthorDetailView(generic.DetailView):
    model = Author
class AllBorrowedBooksListView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing all borrowed books.
    Only visible to users with 'can_mark_returned' permission.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        # Filter for books on loan (status 'o') that have a borrower
        return BookInstance.objects.filter(status__exact='o', borrower__isnull=False).order_by('due_back')
from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})
class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
class BookCreate(CreateView):
    model = Book
    fields = '__all__'
class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from .forms import BookForm, AuthorForm

def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # вернуться на главную
    else:
        form = BookForm()

    return render(request, 'catalog/create_book.html', {'form': form})

def create_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # вернуться на главную
    else:
        form = AuthorForm()

    return render(request, 'catalog/author_form.html', {'form': form})

class AllBorrowedBooksListView(PermissionRequiredMixin, generic.ListView):
    """
    Список всех выданных книг. Доступен только библиотекарям
    с разрешением can_mark_returned.
    """
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/all_borrowed_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')