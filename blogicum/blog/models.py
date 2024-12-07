from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True, verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        abstract = True  # Это делает модель абстрактной


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(unique=True, verbose_name="Идентификатор",
                            help_text="Идентификатор страницы для URL;"
                            " разрешены символы латиницы"
                            ", цифры, дефис и подчёркивание.")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время в будущем — можно делать отложенные публикации.",
        default=timezone.now 
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор публикации", related_name="posts", null=False
    )
    location = models.ForeignKey(
        Location, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="Местоположение", related_name="posts"
    )
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL, verbose_name="Категория", related_name="posts"
    )
    image = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', null=False) 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий под номером {self.pk}"