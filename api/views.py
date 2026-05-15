from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from .models import Item, RentalTransaction
from .serializers import ItemSerializer

# ==========================================
# 🛡️ ROLE-BASED ACCESS CONTROL (RBAC)
# ==========================================
class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission:
    - Allows ANY logged-in user to view data (GET).
    - ONLY allows Admin/Staff users to modify data (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        # If the request is just asking to read data (GET), allow it.
        if request.method in SAFE_METHODS:
            return True
        # If the request is trying to change data, check if they are an admin.
        return bool(request.user and request.user.is_staff)

# ==========================================
# 📦 ITEM MANAGEMENT 
# ==========================================
@api_view(['GET', 'POST'])
# 🔴 FIX: Applied the IsAdminOrReadOnly rule here!
@permission_classes([IsAuthenticated, IsAdminOrReadOnly]) 
def item_list(request):
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_rental_record(request, rental_id):
    try:
        # Find the exact record that belongs to the logged-in user
        rental = RentalTransaction.objects.get(id=rental_id, user=request.user)
        
        # The 'D' in CRUD: Delete the record from the database!
        rental.delete() 
        return Response({"message": "Rental record permanently deleted."}, status=status.HTTP_200_OK)
        
    except RentalTransaction.DoesNotExist:
        return Response({"error": "Record not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

# ==========================================
# 👤 USER AUTHENTICATION & PROFILE
# ==========================================
@api_view(['POST'])
def register_user(request):
    data = request.data
    try:
        if User.objects.filter(username=data['username']).exists():
            return Response({"error": "That Student ID is already registered!"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''), 
            password=data['password']
        )
        
        raw_full_name = data.get('full_name', '').strip()
        if ' ' in raw_full_name:
            first, last = raw_full_name.split(' ', 1)
            user.first_name = first
            user.last_name = last
        else:
            user.first_name = raw_full_name 
            
        user.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# (Note: login_user was removed because SimpleJWT handles it in urls.py now!)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user 
    member_since = user.date_joined.strftime("%B %Y")
    
    return Response({
        "username": user.username,
        "email": user.email,
        "full_name": user.get_full_name().strip() or user.username, 
        "member_since": member_since,
        "trust_score": 100,
        "rentals_count": 0,
        "listings_count": 0,
        "reviews_count": 0
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    try:
        new_username = data.get('username')
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                return Response({"error": "That Student ID is already taken!"}, status=status.HTTP_400_BAD_REQUEST)
            user.username = new_username

        new_full_name = data.get('full_name')
        if new_full_name:
            raw_full_name = new_full_name.strip()
            if ' ' in raw_full_name:
                first, last = raw_full_name.split(' ', 1)
                user.first_name = first
                user.last_name = last
            else:
                user.first_name = raw_full_name
                user.last_name = ""

        new_password = data.get('password')
        if new_password:
            user.set_password(new_password)

        user.save()
        return Response({
            "message": "Profile updated successfully!",
            "username": user.username,
            "full_name": user.get_full_name().strip() or user.username,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==========================================
# 🛒 RENTALS & CHECKOUT
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    item_ids = request.data.get('item_ids', [])
    chosen_locker = request.data.get('locker_id') 
    
    if not item_ids or not chosen_locker:
        return Response({"error": "Missing items or locker selection."}, status=status.HTTP_400_BAD_REQUEST)

    if Item.objects.filter(locker_label=chosen_locker, status='Occupied').exists():
        return Response({"error": f"Locker {chosen_locker} is already in use! Please pick another."}, status=status.HTTP_400_BAD_REQUEST)

    return_date = timezone.now() + timedelta(days=3)
    successful_rentals = 0

    for item_id in item_ids:
        try:
            item = Item.objects.get(id=item_id)
            if item.status == 'Occupied':
                continue 
            
            RentalTransaction.objects.create(
                user=user,
                item=item,
                return_date=return_date,
                total_price=item.price 
            )
            
            item.status = 'Occupied'
            item.locker_label = chosen_locker 
            item.save()
            successful_rentals += 1
        except Item.DoesNotExist:
            continue
            
    if successful_rentals > 0:
        return Response({"message": "Checkout successful!"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Items are no longer available."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_rentals(request):
    rentals = RentalTransaction.objects.filter(user=request.user).order_by('-rental_date')
    
    data = []
    for r in rentals:
        if r.is_returned:
            status_label = "Returned"
        else:
            status_label = "Active" if r.return_date > timezone.now() else "Overdue"

        data.append({
            "id": r.id,
            "item_title": r.item.title,
            "locker_label": r.item.locker_label or "N/A", 
            "rental_date": r.rental_date.strftime("%b %d, %I:%M %p"),
            "return_date": r.return_date.strftime("%b %d, %Y"),
            "status": status_label
        })
        
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_item(request):
    rental_id = request.data.get('rental_id')
    try:
        transaction = RentalTransaction.objects.get(id=rental_id, user=request.user)
        
        if transaction.is_returned:
            return Response({"error": "Item is already returned!"}, status=status.HTTP_400_BAD_REQUEST)
            
        item = transaction.item
        
        item.status = 'Available'
        item.locker_label = None 
        item.save()
        
        transaction.is_returned = True
        transaction.save()
        
        return Response({"message": "Item returned successfully!"}, status=status.HTTP_200_OK)
    except RentalTransaction.DoesNotExist:
        return Response({"error": "Rental not found."}, status=status.HTTP_404_NOT_FOUND)