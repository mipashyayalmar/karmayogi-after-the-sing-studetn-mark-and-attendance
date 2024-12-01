from django.core.paginator import Paginator

@login_required(login_url='login')
def student_inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    paginator = Paginator(messages, 10)  # Show 10 messages per page
    page_number = request.GET.get('page')
    page_messages = paginator.get_page(page_number)
    context = {'messages': page_messages}
    return render(request, 'student/inbox.html', context)
