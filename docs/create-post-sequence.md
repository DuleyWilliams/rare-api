# Create Post — Request Sequence

When an authenticated user navigates to `/posts/new`, the `PostCreate` component loads the available categories on mount, then on submit sends a JSON request to `POST /posts`. The backend sets `user`, `publication_date`, and `approved` server-side before responding with the created post. If the user selected an image, a second `PUT /posts/{id}/image` request follows before navigation to the new post’s detail page.

---

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Browser
    participant AppViews as ApplicationViews.js
    participant PostCreate as PostCreate.js
    participant CatMgr as CategoryManager.js
    participant PostMgr as PostManager.js
    participant APIJS as api.js
    participant Router as Django URL Router
    participant CatView as category_views.category_list
    participant PostView as post_views.post_list
    participant UploadView as post_views.upload_post_image
    participant DB as PostgreSQL

    Browser->>AppViews: navigate to /posts/new
    AppViews->>PostCreate: render PostCreate

    Note over PostCreate,DB: On mount, load categories for the category select

    PostCreate->>CatMgr: getCategories()
    CatMgr->>Router: GET /categories
    Router->>CatView: rareproject/urls.py → rareapi/urls.py → category_list(request)
    CatView-->>Router: 200 [{ id, label }, ...]
    Router-->>PostCreate: category list response

    Note over Browser,PostCreate: User enters title, category, content, and optionally selects an image

    Browser->>PostCreate: submit form → handleSave()
    PostCreate->>PostMgr: createPost({ title, category_id, content })
    PostMgr->>APIJS: authHeader()
    APIJS-->>PostMgr: Authorization header from localStorage token
    PostMgr->>Router: POST /posts with JSON body
    Router->>PostView: rareproject/urls.py → rareapi/urls.py → post_list(request)

    PostView->>DB: Category.objects.get(pk=category_id)
    DB-->>PostView: category record

    Note over PostView: Set user from request.user
    Note over PostView: Set publication_date = timezone.now().date()
    Note over PostView: Set approved = request.user.is_staff

    PostView->>DB: Post.objects.create(...)
    DB-->>PostView: created post

    PostView-->>Router: 201 PostDetailSerializer(post).data
    Router-->>PostCreate: created post response

    alt image file selected
        PostCreate->>PostMgr: uploadPostImage(post.id, formData)
        PostMgr->>APIJS: authHeader()
        APIJS-->>PostMgr: Authorization header from localStorage token
        PostMgr->>Router: PUT /posts/{id}/image with multipart/form-data
        Router->>UploadView: upload_post_image(request, pk)
        UploadView->>UploadView: save file under media/post_images/
        UploadView->>DB: update post.image_url and save
        DB-->>UploadView: updated post
        UploadView-->>Router: 200 { image_url: ... }
        Router-->>PostCreate: image upload response
        PostCreate->>Browser: navigate to /posts/{id}
    else no image selected
        PostCreate->>Browser: navigate to /posts/{id}
    end