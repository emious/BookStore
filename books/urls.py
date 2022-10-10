from django.urls import path
from books import views


urlpatterns = [
    path('v1/booklist', views.BookListApi.as_view()),
    path('v1/loanBookList', views.LoanBookListApi.as_view()),
    path('v1/addBook', views.AddBookApi.as_view()),
    path('v1/detailBook/<int:book_id>', views.book_detail_api),
    path('v1/loanBook', views.loan_book_api),
    path('v1/returnLoanBook', views.return_loan_book_api),
    path('v1/trackLogs', views.track_logs_api),

]
