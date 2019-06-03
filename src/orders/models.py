from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save,post_save
from projects.models import Project
from carts.models import Cart
from earnings.models import Balance
# Create your models here.

import stripe

# STRIPE_SECRET_KEY = getattr(settings,"STRIPE_SECRET_KEY","sk_test_6ETSL1XtldnJi4aM7e8rGqvd009nkra50X")
stripe.api_key = "sk_test_6ETSL1XtldnJi4aM7e8rGqvd009nkra50X"
User = settings.AUTH_USER_MODEL


class BillingManager(models.Manager):
    def new_or_get(self,request):
        user = request.user
        if user.is_authenticated():
            obj,created = self.model.objects.get_or_create(user=user,email=user.email)
        return obj,created


class Billing(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120, null=True, blank=True,)
    email = models.EmailField(max_length=120,null=True,blank=True)
    address = models.CharField(max_length=250, null=True, blank=True,)
    city = models.CharField(max_length=120, null=True, blank=True,)
    country = models.CharField(max_length=120, null=True, blank=True,)
    zipcode = models.IntegerField(null=True, blank=True,)
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120,null=True,blank=True)

    objects = BillingManager()

    def __str__(self):
        return str(self.user)


def billing_profile_created_receiver(sender,instance, *args,**kwargs):
    if not instance.customer_id and instance.email:
        print('Actual Api Key Send To Stripe')
        customer  = stripe.Customer.create(email = instance.email)
        print(customer)
        instance.customer_id = customer.id


pre_save.connect(billing_profile_created_receiver,sender=Billing)


class Card(models.Model):
    billing_profile         = models.ForeignKey(Billing ,on_delete=models.CASCADE )
    stripe_id               = models.CharField(max_length=120)
    brand                   = models.CharField(max_length=120, null=True, blank=True)
    country                 = models.CharField(max_length=20, null=True, blank=True)
    exp_month               = models.IntegerField(null=True, blank=True)
    exp_year                = models.IntegerField(null=True, blank=True)
    last4                   = models.CharField(max_length=4, null=True, blank=True)
    default                 = models.BooleanField(default=True)
    active                  = models.BooleanField(default=True)
    timestamp               = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.stripe_id)


def card_id_create_receiver(sender,instance,*args,**kwargs):
    if instance.billing_profile and instance.stripe_id:
        card = Card.objects.filter(billing_profile=instance.billing_profile).values('stripe_id')
        print(card)
        if not card:
            print('iffff')
            stripe.api_key = 'sk_test_6ETSL1XtldnJi4aM7e8rGqvd009nkra50X'
            customer = stripe.Customer.retrieve(instance.billing_profile.customer_id)
            if customer is not None:
                card_response = customer.sources.create(source=instance.stripe_id)
                instance.stripe_id=card_response.id
                instance.brand = card_response.brand
                instance.country = card_response.country
                instance.exp_month = card_response.exp_month
                instance.exp_year = card_response.exp_year
                instance.last4 = card_response.last4
        else:
            print('else')
            print(f'my obj {card[0]}')
            c = stripe.Customer.delete_source(
                instance.billing_profile.customer_id,
                card[0]['stripe_id']
            )
            Card.objects.filter(billing_profile=instance.billing_profile).delete()
            if c is not None:
                stripe.api_key = 'sk_test_6ETSL1XtldnJi4aM7e8rGqvd009nkra50X'
                customer = stripe.Customer.retrieve(instance.billing_profile.customer_id)
                if customer is not None:
                    card_response = customer.sources.create(source=instance.stripe_id)
                    instance.stripe_id = card_response.id
                    instance.brand = card_response.brand
                    instance.country = card_response.country
                    instance.exp_month = card_response.exp_month
                    instance.exp_year = card_response.exp_year
                    instance.last4 = card_response.last4


pre_save.connect(card_id_create_receiver,sender=Card)


class ChargeManager(models.Manager):
    def do(self,instance):
        q = Card.objects.get(billing_profile=instance.billingAddress)
        c = stripe.Charge.create(
            amount=int(instance.orderTotal * 100),
            currency="usd",
            customer=instance.billingAddress.customer_id,
            source=q.stripe_id,
            metadata={"order_id": instance.user},
        )
        new_charge_obj = self.model(
            billing_profile=instance.billingAddress,
            stripe_id=c.id,
            paid=c.paid,
            refunded=c.refunded,
            outcome=c.outcome,
            outcome_type=c.outcome['type'],
            seller_message=c.outcome.get('seller_message'),
            risk_level=c.outcome.get('risk_level'),
        )
        new_charge_obj.save()
        return new_charge_obj.paid


class Charge(models.Model):
    billing_profile = models.ForeignKey(Billing, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(null=True, blank=True)
    outcome_type = models.CharField(max_length=120, null=True, blank=True)
    seller_message = models.CharField(max_length=120, null=True, blank=True)
    risk_level = models.CharField(max_length=120, null=True, blank=True)

    objects = ChargeManager()


class Order(models.Model):
    user = models.ForeignKey(User , null=True, blank=True, on_delete=models.CASCADE)
    singleProject = models.PositiveIntegerField(default=0,blank=True,null=True)
    project = models.ManyToManyField(Project,blank=True)
    billingAddress = models.ForeignKey(Billing, null= True, blank=True ,on_delete=models.CASCADE)
    status = models.CharField(max_length=250,null=True,blank=True)
    orderTotal = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return str(self.user)


def order_create_receiver(sender,instance,*args,**kwargs):
    if instance.user  and instance.orderTotal:
        try:
            s = Charge.objects.do(instance)
            if s == True:
                instance.status='success'
            else:
                instance.status='pending'
        except Exception as e:
            print(e)


pre_save.connect(order_create_receiver,sender=Order)


def order_save_signal(sender,instance,*args,**kwargs):
    try:
        print(f'Pre_save  {instance.singleProject}')
        if instance.singleProject>0:
            print('IFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
            pro=[instance.singleProject]
            instance.project.add(*pro)
            listDict = [{'projects':instance.singleProject}]
            Balance.objects.add_new(listDict)
        else:
            cart = Cart.objects.filter(user=instance.user).values('projects')
            pro = []
            for item in cart:
                pro.append(item.get('projects'))
            instance.project.add(*pro)
            Balance.objects.add_new(cart)
            Cart.objects.filter(user=instance.user).delete()

    except Exception as e:
        print(e)


post_save.connect(order_save_signal,sender=Order)

