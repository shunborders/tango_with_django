from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm
from rango.forms import UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from registration.backends.simple.views import RegistrationView
from django.contrib.auth.models import User
from rango.bing_search import run_query
from django.shortcuts import redirect

def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response


def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        pages = Page.objects.filter(category=category).order_by('-views')

        context_dict['pages'] = pages

        context_dict['category'] = category

    except category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/Category.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')


def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def add_pages(request, category_name_slug):
    category = Category.objects.get(slug=category_name_slug)
    category_list = {}
    category_list['category_name'] = category.name
    try:
        cat = Category.objects.get(slug=category_name_slug)

    except Category.DoesNotExist:
        cat = none

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                Page = form.save(commit=False)
                Page.category = cat
                Page.views = 0
                Page.save()
                return category(request, category_name_slug)
            else:
                print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'categories': cat}

    return render(request, 'rango/add_pages.html', context_dict)

@login_required
def profile(request):
    usrfirst= request.user.get_short_name
    usrlast= request.user.last_name
    usrname=request.user.username
    usremail= request.user.email
    usrgroups=request.user.get_group_permissions(request.user)
    usrpermissions= request.user.get_all_permissions(request.user)
    usractive=request.user.is_active
    usrsuperusr= request.user.is_superuser
    usrlogin=request.user.last_login
    context_dict = {'first': usrfirst, 'last': usrlast, 'name': usrname, 'email': usremail, 'groups': usrgroups,
                    'permissions': usrpermissions, 'active': usractive, 'super': usrsuperusr, 'login': usrlogin}
    """registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()"""

    return render(request, 'rango/profile.html', context_dict)


"""def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your account is disabled')
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse('Invalid login details supplied')
    else:
        return render(request, 'rango/login.html', {})"""

@login_required
def restricted(request):
    usr = User.objects.all()
    context_dict = {'usrs': usr}
    return render(request, 'rango/restricted.html', context_dict)

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def like_category(request):

    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes =  likes
            cat.save()

    return HttpResponse(likes)




"""def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET'
        if page_id in request.GET:
            page_id=request.GET['page_id']
            try:
                page=Page.objects.get(id=page_id)"""


""""@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')"""