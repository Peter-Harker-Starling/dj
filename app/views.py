from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from .models import Expense
from .ai import ai_parse

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, '註冊成功！你可以登入了～')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', { 'form': form })


@login_required
def add_expense(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        parsed = ai_parse(user_input)

        for item in parsed:
            try:
                amount = abs(float(item.get('amount') or 0)) # 金額用 abs() 強制正數，然後用 float 轉換
                item_name = str(item.get('item', '')).strip() or '未知項目' # 項目名稱如果是空的就用 '未知項目'
                category = item.get('category', '其他') # category 如果沒有就預設 '其他'
                if category not in ['餐飲', '交通', '娛樂', '生活', '其他']:
                    category = '其他'

                Expense.objects.create(
                    user=request.user,
                    expense_date=item['date'],
                    item=item_name,
                    amount=amount,
                    category=category,
                )
            except (ValueError, KeyError):
                messages.error(request, f'「{item.get("item", "某筆資料")}」解析失敗，請重新輸入')
                continue

        messages.success(request, '記帳成功！')
        return redirect('expense_list')
    
    return render(request, 'add_expense.html')


@login_required
def expense_list(request):
    month = request.GET.get('month', datetime.now().strftime('%Y-%m'))

    try:
        year, mon = month.split('-')
        expenses = Expense.objects.filter(
            user=request.user,
            expense_date__year=year,
            expense_date__month=mon,
        )
    except ValueError:
        expenses = Expense.objects.none()

    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    by_category = expenses.values('category').annotate(subtotal=Sum('amount')).order_by('-subtotal')

    return render(request, 'expense_list.html', {
        'expenses': expenses,
        'total': total,
        'by_category': by_category,
        'month': month,
    })

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    if request.method == 'POST':
        try:
            expense.expense_date = request.POST.get('expense_date')
            expense.item = request.POST.get('item', '').strip() or '未知項目'
            expense.amount = abs(float(request.POST.get('amount', 0)))
            category = request.POST.get('category', '其他')
            expense.category = category if category in ['餐飲', '交通', '娛樂', '生活', '其他'] else '其他'
            expense.save()
            messages.success(request, '編輯成功！')
            return redirect('expense_list')
        except (ValueError, KeyError):
            messages.error(request, '資料格式有誤，請重新輸入')
    
    return render(request, 'edit_expense.html', {'expense': expense})

@login_required
def delete_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id, user=request.user)
        expense.delete()
        messages.success(request, '刪除成功！')
    except Expense.DoesNotExist:
        messages.error(request, '找不到該筆記帳資料！')
    
    return redirect(request.META.get('HTTP_REFERER', 'expense_list')) # HTTP_REFERER 會帶使用者回到上一頁，如果沒有就回到 expense_list 頁面