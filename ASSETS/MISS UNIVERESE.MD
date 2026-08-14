If you mean **before vs after improving your downloader**, this is the difference:

| Before — current code            | After — recommended                      |
| -------------------------------- | ---------------------------------------- |
| Downloads first results          | **Collects many candidates first**       |
| Not random                       | **Random selection**                     |
| Pexels/Unsplash can be unrelated | **Actual Miss Universe-focused sources** |
| No image-quality scoring         | **Quality filtering**                    |
| Basic duplicate check            | **Duplicate image detection**            |
| May include blurry/small photos  | **High-resolution filtering**            |
| No portrait/face preference      | **Best-looking portrait preference**     |
| 1,000 images                     | **10,000-image target**                  |
| API result order                 | **Quality score + random selection**     |
| Simple ZIP                       | **Clean image-only ZIP**                 |

### Example

**BEFORE ❌**

```text
Search
 ↓
Image 1 → download
Image 2 → download
Image 3 → download
Image 4 → download
...
Image 1000 → download
 ↓
ZIP
```

You may get:

```text
blurry ❌
generic pageant ❌
duplicate ❌
small image ❌
poster ❌
group photo ❌
good portrait ✅
```

### AFTER ✅

```text
Collect 20,000+ candidates
          ↓
Remove duplicates
          ↓
Resolution filter
          ↓
Blur detection
          ↓
Face/portrait detection
          ↓
Remove posters/logos
          ↓
Quality scoring
          ↓
Randomize among high-quality images
          ↓
Select BEST 10,000
          ↓
ZIP
```

Result:

```text
10,000
   ↓
High resolution ✅
Actual contestants ✅
Good-looking photos ✅
Unique images ✅
Less blur ✅
Portraits/full-body ✅
Only pictures in ZIP ✅
```

**This is the approach I recommend for your Miss Universe dataset.**
