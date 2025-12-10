# SQLAlchemy 2.0 Async Patterns

## Advanced Query Patterns

### Complex Filtering
```python
from sqlalchemy import and_, or_, not_, func

# Multiple conditions
stmt = select(User).where(
    and_(
        User.is_active == True,
        User.email.ilike("%@example.com"),
        User.created_at >= start_date
    )
)

# OR conditions
stmt = select(User).where(
    or_(
        User.username == "admin",
        User.is_superuser == True
    )
)

# NOT condition
stmt = select(User).where(not_(User.is_active))

# IN clause
stmt = select(User).where(User.id.in_([1, 2, 3]))

# LIKE/ILIKE
stmt = select(User).where(User.email.ilike("%example%"))

# NULL checks
stmt = select(User).where(User.phone.is_(None))
stmt = select(User).where(User.phone.isnot(None))
```

### Aggregation
```python
from sqlalchemy import func, desc

# Count
count_stmt = select(func.count(User.id))
total = await db.scalar(count_stmt)

# Group by
stmt = (
    select(User.country, func.count(User.id))
    .group_by(User.country)
    .having(func.count(User.id) > 5)
)

# Max/Min/Avg
stmt = select(func.max(Post.created_at), func.count(Post.id))
```

### Joins
```python
# Inner join
stmt = (
    select(Post, User)
    .join(User, Post.author_id == User.id)
)

# Left outer join
stmt = (
    select(User, Post)
    .outerjoin(Post, User.id == Post.author_id)
)

# Multiple joins
stmt = (
    select(Comment, Post, User)
    .join(Post, Comment.post_id == Post.id)
    .join(User, Post.author_id == User.id)
)
```

### Subqueries
```python
# Subquery
subq = (
    select(func.count(Post.id).label("post_count"), Post.author_id)
    .group_by(Post.author_id)
    .subquery()
)

stmt = (
    select(User, subq.c.post_count)
    .outerjoin(subq, User.id == subq.c.author_id)
)
```

## Relationship Loading Strategies

### selectinload (Recommended for One-to-Many)
```python
# Loads related objects in separate query
stmt = select(User).options(selectinload(User.posts))
```

### joinedload (For Many-to-One, One-to-One)
```python
# Loads related objects with JOIN
stmt = select(Post).options(joinedload(Post.author))
```

### Nested Loading
```python
stmt = (
    select(User)
    .options(
        selectinload(User.posts)
        .selectinload(Post.comments)
    )
)
```

## Bulk Operations

### Bulk Insert
```python
users = [
    User(email=f"user{i}@example.com", username=f"user{i}")
    for i in range(100)
]
db.add_all(users)
await db.commit()
```

### Bulk Update
```python
from sqlalchemy import update

stmt = (
    update(User)
    .where(User.is_active == False)
    .values(is_active=True)
)
await db.execute(stmt)
await db.commit()
```

## Connection Pooling

### Configuration
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,          # Number of persistent connections
    max_overflow=10,      # Additional connections allowed
    pool_timeout=30,      # Timeout waiting for connection
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_pre_ping=True    # Test connections before use
)
```

## Performance Optimization

### Use compiled queries
```python
# Cache compiled statement
compiled = select(User).where(User.id == bindparam("user_id")).compile(compile_kwargs={"literal_binds": True})
```

### Batch loading
```python
# Load multiple objects efficiently
user_ids = [1, 2, 3, 4, 5]
stmt = select(User).where(User.id.in_(user_ids))
users = await db.scalars(stmt)
```

### Defer loading heavy columns
```python
from sqlalchemy.orm import defer

stmt = select(User).options(defer(User.large_data_field))
```

## Error Handling

```python
from sqlalchemy.exc import IntegrityError, DBAPIError

try:
    user = User(email=email, username=username)
    db.add(user)
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    raise HTTPException(409, "User already exists")
except DBAPIError as e:
    await db.rollback()
    raise HTTPException(500, "Database error")
```
