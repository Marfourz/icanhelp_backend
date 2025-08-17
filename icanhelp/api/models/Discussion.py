from django.db import models

class Discussion(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)

    updatedAt = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100,default='')
    
    createdBy = models.ForeignKey(
        'api.UserProfil', related_name="createDiscussions", blank=False, on_delete=models.CASCADE,
    )

    users = models.ManyToManyField(
        'api.UserProfil', blank=True, related_name="discussions"
    )

    lastMessage = models.ForeignKey(
        'api.Message', blank=True, on_delete=models.SET_NULL,null=True,related_name="discussion_of_last"
    )

    class Meta:
        ordering = ['createdAt']

    @classmethod
    def get_or_create_between(cls, user1, user2):
        # Récupère les discussions où les deux users sont dedans
        discussions = cls.objects.filter(users__in=[user1, user2]).distinct()

        for discussion in discussions:
            users_set = set(discussion.users.all())
            if users_set == {user1, user2}:
                return discussion

        # Sinon, on crée
        discussion = cls.objects.create(createdBy=user1)
        discussion.users.set([user1, user2])
        return discussion