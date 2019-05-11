from django.db import models
from django.conf import settings
from projects.models import Project
# Create your models here.
User = settings.AUTH_USER_MODEL


class BalanceManager(models.Manager):
    def add_new(self, cart):
       try:
           for i in cart:
               p_id = i.get('projects')
               p_qs = Project.objects.get(id=p_id)
               SoldSoftwares.objects.new_add(user=p_qs.user, project=p_qs, price=p_qs.price)
               b_qs = Balance.objects.filter(user=p_qs.user)
               if b_qs:
                    balance = b_qs[0].balance
                    balance += p_qs.price - p_qs.service_fees
                    u_qs = Balance.objects.filter(user=p_qs.user).update(balance=balance)
               else:
                    c_qs = Balance.objects.create(user=p_qs.user, balance=p_qs.price - p_qs.service_fees)
       except Exception as e:
           print(e)


class Balance(models.Model):
    user    = models.OneToOneField(User,on_delete=models.CASCADE)
    balance = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects=BalanceManager()

    def __str__(self):
        return str(self.user)


class SoldSoftwareManager(models.Manager):
    def new_add(self, user, project, price):
        new_instance = self.model(
            user=user,
            project=project,
            sold_price=price
        )
        new_instance.save()
        return new_instance


class SoldSoftwares(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sold_price = models.PositiveIntegerField(blank=True, null=True)
    category = models.CharField(max_length=50, default='Desktop')
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = SoldSoftwareManager()

    def __str__(self):
        return str(self.project)


class SaleSummary(SoldSoftwares):
    class Meta:
        proxy = True
        verbose_name = 'Sale Summary'
        verbose_name_plural = 'Sales Summary'









