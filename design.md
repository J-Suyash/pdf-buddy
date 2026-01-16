# Question Paper Search Engine - Figma Design Specification

## Design Philosophy

### Core Principles
1. **Clarity Over Complexity**: Clean, focused interfaces that guide users through tasks
2. **Progressive Disclosure**: Show complexity only when needed
3. **Immediate Feedback**: Real-time status updates and visual confirmation
4. **Academic Aesthetic**: Professional, trustworthy design suitable for educational context
5. **Performance-First**: Fast-loading, lightweight components using shadcn/ui

### Design System Foundation

#### Color Palette
```
Primary (Indigo):
- 50:  #EEF2FF (Backgrounds, hover states)
- 100: #E0E7FF (Light accents)
- 500: #6366F1 (Primary actions, links)
- 600: #4F46E5 (Hover states)
- 700: #4338CA (Active states)
- 900: #312E81 (Dark text)

Neutral (Slate):
- 50:  #F8FAFC (Page backgrounds)
- 100: #F1F5F9 (Card backgrounds)
- 200: #E2E8F0 (Borders)
- 400: #94A3B8 (Placeholder text)
- 600: #475569 (Secondary text)
- 900: #0F172A (Primary text)

Success (Emerald):
- 50:  #ECFDF5 (Success backgrounds)
- 500: #10B981 (Success states)
- 600: #059669 (Success hover)

Warning (Amber):
- 50:  #FFFBEB (Warning backgrounds)
- 500: #F59E0B (Warning states)

Error (Red):
- 50:  #FEF2F2 (Error backgrounds)
- 500: #EF4444 (Error states)
- 600: #DC2626 (Error hover)

Semantic Colors:
- Processing: #3B82F6 (Blue-500)
- Queued: #A855F7 (Purple-500)
- Completed: #10B981 (Emerald-500)
- Failed: #EF4444 (Red-500)
```

#### Typography
```
Font Family: Inter (primary), JetBrains Mono (code/monospace)

Headings:
- H1: 36px / 40px, Weight 700, Letter-spacing -0.02em
- H2: 30px / 36px, Weight 700, Letter-spacing -0.01em
- H3: 24px / 32px, Weight 600
- H4: 20px / 28px, Weight 600
- H5: 16px / 24px, Weight 600

Body:
- Large: 18px / 28px, Weight 400
- Base:  16px / 24px, Weight 400
- Small: 14px / 20px, Weight 400
- XS:    12px / 16px, Weight 400

Special:
- Code: JetBrains Mono, 14px, Weight 400
- Caption: 12px / 16px, Weight 500, Letter-spacing 0.03em, Uppercase
```

#### Spacing System
```
Base unit: 4px

Scale:
- 1:  4px   (xs)
- 2:  8px   (sm)
- 3:  12px  (md)
- 4:  16px  (base)
- 5:  20px  
- 6:  24px  (lg)
- 8:  32px  (xl)
- 10: 40px  (2xl)
- 12: 48px  (3xl)
- 16: 64px  (4xl)
- 20: 80px  (5xl)
- 24: 96px  (6xl)
```

#### Border Radius
```
- sm: 4px   (buttons, inputs)
- md: 6px   (cards, small components)
- lg: 8px   (large cards)
- xl: 12px  (modals, drawers)
- 2xl: 16px (hero sections)
- full: 9999px (pills, avatars)
```

#### Shadows
```
- sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
- md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
- lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
- xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)
```

---

## Page Designs

### 1. Landing Page / Home
**Route**: `/`
**Purpose**: First impression, explain value proposition, primary entry point

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│                    Navigation Bar                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│                      Hero Section                         │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│                    Features Grid                          │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│                   How It Works                            │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│                  Statistics Section                       │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                       Footer                              │
└─────────────────────────────────────────────────────────┘
```

#### Navigation Bar
**Dimensions**: Full width, 72px height
**Position**: Fixed top, with blur backdrop
**Background**: Slate-50/80 with backdrop-blur-lg
**Border**: Bottom 1px Slate-200

**Components**:
```
┌─────────────────────────────────────────────────────────┐
│ [Logo + Name]           [Search] [Upload] [Analytics]   │
│                                                  [Theme] │
└─────────────────────────────────────────────────────────┘
```

**Logo Section** (Left):
- Icon: Custom graduation cap with search glass overlay (24x24px)
- Text: "QuestionBank" in Inter 600, 18px, Slate-900
- Spacing: 12px gap between icon and text
- Padding: 24px left

**Navigation Links** (Center-Right):
- Buttons: Ghost variant (shadcn)
- Size: 40px height, 16px font
- Spacing: 8px gap between items
- States:
  - Default: Slate-600 text
  - Hover: Slate-900 text, Slate-100 background
  - Active: Indigo-600 text, Indigo-50 background

**Theme Toggle** (Far Right):
- Icon button: Sun/Moon icon
- Size: 40x40px
- Position: 24px from right edge

#### Hero Section
**Dimensions**: Full width, 600px height (desktop)
**Background**: Gradient from Slate-50 to Indigo-50/30
**Padding**: 80px top, 120px bottom

**Layout**:
```
                [Centered Content]
                
        Find Your Perfect Question
          in Seconds, Not Hours
        
        [Subtitle explaining semantic search]
        
        [Upload Button]  [Try Demo Search]
        
              [Visual Demo/Animation]
```

**Main Heading**:
- Text: "Find Your Perfect Question in Seconds, Not Hours"
- Typography: H1 (36px), Weight 700, Slate-900
- Max-width: 800px, centered
- Line-height: 1.2
- Margin-bottom: 24px

**Subtitle**:
- Text: "AI-powered semantic search through 10,000+ university question papers. Upload your PDFs or search instantly."
- Typography: Body Large (18px), Slate-600
- Max-width: 600px, centered
- Line-height: 1.6
- Margin-bottom: 40px

**CTA Buttons**:
- Primary: "Upload Question Papers" 
  - Size: 48px height, 180px width
  - Background: Indigo-600
  - Text: White, 16px, Weight 600
  - Border-radius: 8px
  - Shadow: lg
  - Hover: Indigo-700, shadow-xl, translate-y -1px
  
- Secondary: "Try Demo Search"
  - Size: 48px height, 160px width
  - Variant: Outline (Indigo-600 border)
  - Text: Indigo-600, 16px, Weight 600
  - Hover: Indigo-50 background

- Spacing: 16px gap between buttons

**Visual Element**:
- Floating search bar mockup with animated results
- Position: Below CTAs, 60px margin-top
- Dimensions: 700px width, 400px height
- Design: Glassmorphic card showing search interface
- Animation: Typewriter effect on search query, smooth result appearance

#### Features Grid
**Dimensions**: Full width container (max-width: 1200px)
**Padding**: 120px vertical, 24px horizontal
**Background**: White

**Section Header**:
- Title: "Everything You Need" (H2, Slate-900)
- Subtitle: "Powerful features to accelerate your exam preparation"
- Alignment: Center
- Margin-bottom: 64px

**Grid Layout**: 3 columns (desktop), 1 column (mobile)
**Gap**: 32px horizontal, 48px vertical

**Feature Card** (repeating component):
```
┌────────────────────────────┐
│         [Icon]             │
│                            │
│    [Feature Title]         │
│                            │
│  [Feature Description]     │
│                            │
│     [Learn More →]         │
└────────────────────────────┘
```

**Card Styling**:
- Size: Auto width, min-height 280px
- Background: Slate-50
- Border: 1px Slate-200
- Border-radius: 12px
- Padding: 32px
- Hover: Translate-y -4px, shadow-xl, border Indigo-200
- Transition: All 0.3s ease

**Icon Container**:
- Size: 48x48px
- Background: Indigo-100
- Border-radius: 12px
- Icon: 24x24px, Indigo-600
- Margin-bottom: 20px

**Title**:
- Typography: H4 (20px), Weight 600, Slate-900
- Margin-bottom: 12px

**Description**:
- Typography: Body Small (14px), Slate-600
- Line-height: 1.6
- Margin-bottom: 20px

**Learn More Link**:
- Text: "Learn more →"
- Color: Indigo-600
- Typography: 14px, Weight 500
- Hover: Indigo-700, underline

**6 Features to showcase**:

1. **Semantic Search**
   - Icon: Search with sparkles
   - Title: "Smart Semantic Search"
   - Description: "Find questions by meaning, not just keywords. Our AI understands context and intent."

2. **Instant Upload**
   - Icon: Cloud upload with lightning
   - Title: "Lightning-Fast Processing"
   - Description: "Upload multiple PDFs simultaneously. Processing starts in seconds with real-time progress."

3. **Advanced Filters**
   - Icon: Funnel with settings
   - Title: "Powerful Filtering"
   - Description: "Filter by year, subject, difficulty, and question type. Find exactly what you need."

4. **Question Clustering**
   - Icon: Network nodes
   - Title: "Topic Clustering"
   - Description: "Automatically groups similar questions. See patterns and focus your study."

5. **Analytics Dashboard**
   - Icon: Bar chart
   - Title: "Study Analytics"
   - Description: "Track your searches, discover trending topics, and optimize your preparation."

6. **Export & Share**
   - Icon: Share network
   - Title: "Export Results"
   - Description: "Download search results as PDF. Create custom question sets for practice."

#### How It Works Section
**Dimensions**: Full width, max-width 1400px
**Background**: Gradient Indigo-50 to Slate-50
**Padding**: 120px vertical

**Layout**: Alternating image-text blocks (3 steps)

**Section Header**:
- Title: "How It Works" (H2)
- Subtitle: "Three simple steps to smarter studying"
- Alignment: Center
- Margin-bottom: 80px

**Step Card Layout**:
```
Step 1 (Image Left):
┌──────────────┬──────────────┐
│              │  [Step 1]    │
│   [Visual]   │  [Title]     │
│              │  [Desc]      │
└──────────────┴──────────────┘

Step 2 (Image Right):
┌──────────────┬──────────────┐
│  [Step 2]    │              │
│  [Title]     │   [Visual]   │
│  [Desc]      │              │
└──────────────┴──────────────┘

Step 3 (Image Left):
┌──────────────┬──────────────┐
│              │  [Step 3]    │
│   [Visual]   │  [Title]     │
│              │  [Desc]      │
└──────────────┴──────────────┘
```

**Step Component Styling**:

*Step Badge*:
- Text: "STEP 01", "STEP 02", "STEP 03"
- Typography: Caption (12px), Weight 600, Uppercase
- Color: Indigo-600
- Background: Indigo-50
- Padding: 6px 12px
- Border-radius: 999px
- Margin-bottom: 16px

*Title*:
- Typography: H3 (24px), Weight 600, Slate-900
- Margin-bottom: 16px

*Description*:
- Typography: Body Base (16px), Slate-600
- Line-height: 1.6
- Max-width: 500px

*Visual Container*:
- Size: 600x400px
- Background: White
- Border-radius: 16px
- Shadow: xl
- Padding: 24px
- Contains: Mockup screenshot or illustration

**3 Steps**:

1. **Upload Your Papers**
   - Visual: Drag-drop upload interface with progress
   - Description: "Simply drag and drop your PDF question papers. We'll process them in the background using AI extraction."

2. **AI Processing**
   - Visual: Animated processing pipeline diagram
   - Description: "Our AI extracts questions, categorizes by topic, and creates semantic embeddings for intelligent search."

3. **Search & Study**
   - Visual: Search interface with results
   - Description: "Search naturally using any keywords. Get relevant questions instantly with smart filters and recommendations."

#### Statistics Section
**Dimensions**: Full width, max-width 1200px
**Background**: White
**Padding**: 100px vertical

**Layout**: 4 columns grid (responsive)

```
┌──────────┬──────────┬──────────┬──────────┐
│  [Stat]  │  [Stat]  │  [Stat]  │  [Stat]  │
└──────────┴──────────┴──────────┴──────────┘
```

**Stat Card**:
- Alignment: Center
- Spacing: 24px gap

*Number*:
- Typography: 48px, Weight 700, Indigo-600
- Animation: Count-up on viewport entry

*Label*:
- Typography: Body Base (16px), Slate-600
- Margin-top: 8px

*Icon* (optional):
- Size: 20x20px above number
- Color: Indigo-400

**4 Statistics**:
1. "12,450+ Questions Indexed"
2. "234 Papers Processed"
3. "<50ms Average Search Time"
4. "99.9% Uptime"

#### Footer
**Dimensions**: Full width
**Background**: Slate-900
**Padding**: 64px vertical, 24px horizontal

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│  [About]     [Features]    [Resources]    [Legal]   │
│                                                      │
│            [Social Links]                            │
│                                                      │
│      © 2025 QuestionBank. Built with Claude.        │
└─────────────────────────────────────────────────────┘
```

**Column Styling**:
- Text Color: Slate-400
- Link Hover: White
- Typography: 14px
- Line-height: 2

**Social Links**:
- Icons: GitHub, Twitter/X, LinkedIn
- Size: 24x24px
- Color: Slate-400
- Hover: Indigo-400

---

### 2. Upload Page
**Route**: `/upload`
**Purpose**: PDF upload interface with job management

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│                    Navigation Bar                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│                   Upload Zone (Large)                     │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│                  Active Jobs List                         │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Page Container
**Max-width**: 1400px
**Padding**: 40px horizontal, 40px top
**Background**: Slate-50

#### Page Header
**Margin-bottom**: 40px

*Title*:
- Text: "Upload Question Papers"
- Typography: H2 (30px), Weight 700, Slate-900

*Subtitle*:
- Text: "Upload single or multiple PDF files. Processing starts automatically."
- Typography: Body Base (16px), Slate-600
- Margin-top: 8px

#### Upload Zone
**Dimensions**: Full width, 400px height (empty state)
**Position**: Sticky top on scroll
**Background**: White
**Border**: 2px dashed Slate-300
**Border-radius**: 16px
**Padding**: 60px

**States**:

**1. Empty State (Default)**
```
┌────────────────────────────────────────────┐
│                                             │
│              [Upload Icon]                  │
│                                             │
│        Drag and drop PDFs here             │
│              or click to browse             │
│                                             │
│   [Browse Files Button]                     │
│                                             │
│   Accepts: PDF | Max size: 50MB per file   │
│                                             │
└────────────────────────────────────────────┘
```

*Icon*:
- Design: Cloud with upward arrow
- Size: 64x64px
- Color: Slate-400
- Margin-bottom: 24px

*Main Text*:
- Typography: Body Large (18px), Weight 500, Slate-700
- Alignment: Center

*Secondary Text*:
- Typography: Body Base (16px), Slate-500
- Margin-top: 8px

*Browse Button*:
- Size: 44px height, 160px width
- Variant: Outline
- Text: "Browse Files"
- Margin-top: 24px

*File Info*:
- Typography: Body Small (14px), Slate-400
- Margin-top: 20px

**2. Hover State**
- Border: 2px dashed Indigo-400
- Background: Indigo-50/50
- Icon: Indigo-500
- Text: Indigo-700
- Scale: 1.01
- Transition: All 0.2s

**3. Drag Active State**
- Border: 2px solid Indigo-500
- Background: Indigo-100/50
- Scale: 1.02
- Glow: 0 0 0 4px Indigo-100

**4. Files Selected State**
```
┌────────────────────────────────────────────┐
│  [✓] Files Ready to Upload                 │
│                                             │
│  ┌──────────────────────────────────┐     │
│  │ 📄 exam_2023.pdf          2.4MB  │     │
│  │ 📄 midterm_2022.pdf       1.8MB  │     │
│  │ 📄 final_2021.pdf         3.1MB  │     │
│  └──────────────────────────────────┘     │
│                                             │
│  [Add More Files] [Upload All (3 files)]   │
└────────────────────────────────────────────┘
```

**Height**: Auto (expands with files)
**Max-height**: 500px with scroll

*Success Header*:
- Icon: Checkmark circle (Emerald-500)
- Text: "Files Ready to Upload"
- Typography: Body Base (16px), Weight 600, Slate-900
- Background: Emerald-50
- Padding: 12px 20px
- Border-radius: 8px 8px 0 0

*File List*:
- Background: Slate-50
- Border-radius: 8px
- Padding: 12px
- Max-height: 300px, overflow-y: auto

*File Item*:
```
┌────────────────────────────────────────┐
│ 📄 [Filename]                  [Size]  │
│    [Progress Bar] 45%           [×]    │
└────────────────────────────────────────┘
```

- Height: 60px
- Padding: 12px 16px
- Background: White
- Border: 1px Slate-200
- Border-radius: 6px
- Margin-bottom: 8px

*File Icon*:
- Emoji or PDF icon
- Size: 24x24px

*Filename*:
- Typography: 14px, Weight 500, Slate-900
- Truncate: text-overflow ellipsis

*File Size*:
- Typography: 12px, Slate-500
- Position: Right aligned

*Remove Button*:
- Icon: X (close)
- Size: 20x20px
- Color: Slate-400
- Hover: Red-500
- Position: Absolute right

*Action Buttons*:
- Layout: Flex, justify space-between
- Margin-top: 20px

- "Add More Files": Ghost variant, Slate-600
- "Upload All": Primary, Indigo-600, with file count

**5. Uploading State**
```
┌────────────────────────────────────────────┐
│  ⏳ Uploading 3 files...                   │
│                                             │
│  📄 exam_2023.pdf                           │
│  ████████████░░░░░░░░  65%                  │
│                                             │
│  📄 midterm_2022.pdf                        │
│  ██████████████████░░  100% ✓              │
│                                             │
│  📄 final_2021.pdf                          │
│  ████░░░░░░░░░░░░░░░░  25%                  │
│                                             │
│  [Cancel Upload]                            │
└────────────────────────────────────────────┘
```

*Progress Bar Component*:
- Height: 8px
- Background: Slate-200
- Fill: Indigo-500 (active), Emerald-500 (complete)
- Border-radius: 999px
- Animated: Progress transition 0.3s ease

*Status Icons*:
- Uploading: Animated spinner
- Completed: Green checkmark
- Failed: Red X with retry button

**6. Success State**
```
┌────────────────────────────────────────────┐
│  ✓ Upload Complete!                        │
│                                             │
│  3 files uploaded successfully             │
│  Processing has started...                 │
│                                             │
│  [View Jobs] [Upload More Files]           │
└────────────────────────────────────────────┘
```

- Background: Emerald-50
- Border: 2px solid Emerald-500
- Icon: Large checkmark (Emerald-500, 48px)
- Auto-dismiss after 5s or manual close

#### Active Jobs Section
**Position**: Below upload zone
**Margin-top**: 48px

**Section Header**:
```
[Title: "Your Upload Jobs"]    [Filter Dropdown]
```

- Typography: H3 (24px), Weight 600, Slate-900
- Filter: "All", "Processing", "Completed", "Failed"

**Jobs Layout**: Grid 2 columns (desktop), 1 column (mobile)
**Gap**: 24px

#### Job Card Component
```
┌─────────────────────────────────────────────┐
│ [Status Badge]                      [Menu]  │
│                                             │
│ Job ID: abc-123-def                         │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ 📄 exam_2023.pdf          2.4MB     │   │
│ │ 📄 midterm_2022.pdf       1.8MB     │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ [Progress Bar] 65%                          │
│                                             │
│ Status: Extracting questions...             │
│ Started: 2 minutes ago                      │
│                                             │
│ [View Details] [Cancel Job]                 │
└─────────────────────────────────────────────┘
```

**Card Styling**:
- Background: White
- Border: 1px Slate-200
- Border-radius: 12px
- Padding: 24px
- Shadow: sm

**Section Headers**:
- Typography: 14px, Weight 600, Uppercase, Slate-500
- Margin-bottom: 16px
- Letter-spacing: 0.05em

**Data Rows**:
- Layout: Key-value pairs
- Gap: 12px vertical
- Key: 14px, Slate-600
- Value: 14px, Weight 600, Slate-900

**Divider**:
- Border: 1px Slate-200
- Margin: 20px vertical

**Results Metrics**:
- Icon + Number + Label layout
- Number: 24px, Weight 700, Indigo-600
- Label: 12px, Slate-600
- Spacing: 16px vertical between items

**Files List Card**:
```
┌────────────────────────────────┐
│  Files (3)                     │
│                                │
│  📄 exam_2023.pdf              │
│     2.4MB • 28 pages           │
│     ✓ 89 questions extracted   │
│                                │
│  📄 midterm_2022.pdf           │
│     1.8MB • 22 pages           │
│     ✓ 67 questions extracted   │
│                                │
│  📄 final_2021.pdf             │
│     3.1MB • 37 pages           │
│     ✓ 89 questions extracted   │
│                                │
└────────────────────────────────┘
```

**Same card styling as Job Info**
**Margin-top**: 24px

**File Item**:
- Padding: 16px
- Background: Slate-50
- Border-radius: 8px
- Margin-bottom: 12px
- Hover: Slate-100, cursor pointer

*File Name*:
- Typography: 14px, Weight 600, Slate-900

*File Meta*:
- Typography: 12px, Slate-500
- Margin-top: 4px

*Extraction Status*:
- Typography: 12px, Weight 500
- Color: Emerald-600 (success), Red-600 (error)
- Icon: Checkmark or X
- Margin-top: 4px

#### Right Column - Processing Timeline

**Timeline Card**:
```
┌──────────────────────────────────────────┐
│  Processing Timeline                      │
│                                           │
│  ● Uploaded                               │
│  │ Jan 15, 2025 at 2:30:15 PM           │
│  │ Files received and validated          │
│  │                                        │
│  ● Job Queued                             │
│  │ Jan 15, 2025 at 2:30:16 PM           │
│  │ Added to processing queue             │
│  │                                        │
│  ● Processing Started                     │
│  │ Jan 15, 2025 at 2:30:18 PM           │
│  │ Extracting text from PDFs...          │
│  │                                        │
│  ● PDF Extraction Complete                │
│  │ Jan 15, 2025 at 2:31:45 PM           │
│  │ Extracted 87 pages from 3 files       │
│  │                                        │
│  ● AI Question Detection                  │
│  │ Jan 15, 2025 at 2:31:47 PM           │
│  │ Identifying questions using LlamaCloud│
│  │ [Progress: 100%]                       │
│  │                                        │
│  ● Generating Embeddings                  │
│  │ Jan 15, 2025 at 2:32:23 PM           │
│  │ Creating semantic embeddings...        │
│  │ [Progress: 100%]                       │
│  │                                        │
│  ● Indexing Complete                      │
│  │ Jan 15, 2025 at 2:32:49 PM           │
│  │ 245 questions indexed in Qdrant       │
│  │                                        │
│  ✓ Job Completed                          │
│    Jan 15, 2025 at 2:32:49 PM           │
│    Ready for search!                      │
│                                           │
└──────────────────────────────────────────┘
```

**Card Styling**: Same as left column cards
**Min-height**: 600px

**Timeline Item Structure**:

*Status Indicator* (Dot):
- Size: 12x12px circle
- Colors:
  - Completed: Emerald-500
  - Active: Blue-500 (pulsing animation)
  - Pending: Slate-300
  - Failed: Red-500

*Connecting Line*:
- Width: 2px
- Color: Slate-200
- Left: 6px from dot center
- Length: To next item

*Timestamp*:
- Typography: 14px, Weight 600, Slate-900
- Margin-bottom: 4px

*Description*:
- Typography: 13px, Slate-600
- Line-height: 1.5
- Margin-bottom: 8px

*Progress Bar* (for active items):
- Width: 100%
- Height: 6px
- Background: Slate-200
- Fill: Blue-500
- Border-radius: 999px
- Margin-top: 8px
- Animated gradient for active processing

*Meta Info*:
- Typography: 12px, Slate-500
- Font: JetBrains Mono (for technical details)

**Error State** (if job failed):
```
  ✗ Processing Failed
  │ Jan 15, 2025 at 2:31:30 PM
  │ 
  │ ┌────────────────────────────┐
  │ │ ⚠ Error Details            │
  │ │                            │
  │ │ LlamaCloud API timeout     │
  │ │ Error code: ETIMEDOUT      │
  │ │                            │
  │ │ [Retry Job] [View Logs]    │
  │ └────────────────────────────┘
```

**Error Box**:
- Background: Red-50
- Border: 1px Red-200
- Border-radius: 8px
- Padding: 16px

#### Questions Preview Section
**Position**: Below main grid
**Margin-top**: 32px
**Padding**: 40px horizontal

**Section Card**:
```
┌──────────────────────────────────────────────────────────┐
│  Extracted Questions (245)        [Search] [Filter] [⚙]  │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  [Filters Row: All | Subject | Year | Difficulty | Type]  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Question 1                                         │  │
│  │ Explain the concept of binary search tree...      │  │
│  │                                                     │  │
│  │ 📚 Data Structures • 📅 2023 • ⭐ Medium          │  │
│  │ 📄 exam_2023.pdf (Page 5)                         │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  [... more question cards ...]                            │
│                                                            │
│  [Load More Questions]                                     │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

**Card Styling**: White background, full width

**Header Section**:
- Layout: Flex row, space-between
- Padding: 24px
- Border-bottom: 1px Slate-200

*Title*:
- Typography: H3 (24px), Weight 600, Slate-900
- Count in parentheses

*Actions*:
- Search input: 240px width, Ghost variant
- Filter button: Icon button
- Settings: Dropdown (export, download, etc.)

**Filter Pills Row**:
- Padding: 16px 24px
- Background: Slate-50
- Border-bottom: 1px Slate-200
- Gap: 8px
- Horizontal scroll on mobile

**Filter Pill**:
- Size: 36px height, Auto width
- Padding: 8px 16px
- Border-radius: 999px
- Typography: 14px, Weight 500

*States*:
- Default: Slate-200 bg, Slate-700 text
- Active: Indigo-600 bg, White text
- Hover: Slate-300 bg

**Question Card**:
```
┌────────────────────────────────────────────┐
│  Q1                                  [•••] │
│                                            │
│  [Question Text - Max 3 lines with...]    │
│                                            │
│  📚 Subject • 📅 Year • ⭐ Difficulty     │
│  📄 Source File (Page X)                  │
│                                            │
│  [View Full] [Similar Questions]          │
└────────────────────────────────────────────┘
```

**Card Styling**:
- Padding: 20px 24px
- Border-bottom: 1px Slate-200
- Hover: Background Slate-50

*Question Number*:
- Typography: 12px, Weight 600, Slate-500
- Background: Slate-100
- Padding: 4px 8px
- Border-radius: 4px

*Question Text*:
- Typography: 16px, Slate-900, Line-height 1.6
- Max-height: 4.8em (3 lines)
- Overflow: ellipsis

*Metadata Tags*:
- Layout: Flex row, gap 12px
- Typography: 13px, Slate-600
- Margin-top: 12px
- Icons: 16x16px inline

*Source Info*:
- Typography: 12px, Slate-500
- Margin-top: 8px

*Actions*:
- Layout: Flex row, gap 12px
- Buttons: Ghost variant, Small size
- Margin-top: 16px

**Load More Button**:
- Position: Center, bottom of list
- Size: 44px height, 180px width
- Variant: Outline
- Margin: 32px auto

---

### 4. Search Page
**Route**: `/search`
**Purpose**: Main search interface with filters and results

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│                    Navigation Bar                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│              [Large Search Bar with Filters]              │
│                                                           │
├───────────────┬─────────────────────────────────────────┤
│               │                                          │
│   Filter      │        Search Results                   │
│   Sidebar     │                                          │
│               │                                          │
│               │                                          │
└───────────────┴─────────────────────────────────────────┘
```

#### Page Container
**Background**: Slate-50
**Padding**: 0px (full width for search bar section)

#### Search Header Section
**Background**: White
**Padding**: 40px horizontal, 32px vertical
**Border-bottom**: 1px Slate-200
**Sticky**: Top after scroll (with blur backdrop)

**Search Bar**:
```
┌──────────────────────────────────────────────────────┐
│  🔍  [Search for questions...]          [Search]    │
└──────────────────────────────────────────────────────┘
```

**Dimensions**: Max-width 900px, centered
**Height**: 56px
**Background**: Slate-50
**Border**: 1px Slate-300
**Border-radius**: 12px
**Shadow**: sm
**Focus**: Border Indigo-500, shadow-lg

**Search Icon**:
- Size: 20x20px
- Color: Slate-400
- Position: Left, 16px padding

**Input Field**:
- Typography: 16px, Slate-900
- Placeholder: Slate-400
- Flex: 1
- No border

**Search Button**:
- Size: 44px height, 100px width
- Background: Indigo-600
- Text: White, 15px, Weight 600
- Border-radius: 8px
- Margin: 6px from edge
- Hover: Indigo-700
- Keyboard shortcut: ⌘K hint

**Quick Filters** (Below search bar):
**Margin-top**: 20px
**Layout**: Flex row, gap 8px, center aligned

```
[All Results] [This Year] [Medium] [MCQ] [Data Structures]
```

**Quick Filter Chip**:
- Size: 32px height
- Padding: 6px 14px
- Background: White
- Border: 1px Slate-300
- Border-radius: 999px
- Typography: 13px, Weight 500, Slate-700
- Hover: Indigo-50, Border Indigo-300
- Active: Indigo-600 bg, White text

#### Main Content Area
**Layout**: Grid with sidebar
**Padding**: 32px horizontal, 24px vertical
**Gap**: 32px
**Max-width**: 1600px, centered

#### Left Sidebar - Filters
**Width**: 280px (fixed)
**Position**: Sticky top
**Background**: White
**Border-radius**: 12px
**Padding**: 24px
**Shadow**: sm
**Max-height**: calc(100vh - 200px)
**Overflow**: Auto with custom scrollbar

**Filter Section Structure**:
```
┌──────────────────────────┐
│  Filters          [Clear]│
├──────────────────────────┤
│                          │
│  Subject                 │
│  [Checkbox List]         │
│                          │
│  ────────────────        │
│                          │
│  Year                    │
│  [Range Slider]          │
│                          │
│  ────────────────        │
│                          │
│  Difficulty              │
│  [Radio Group]           │
│                          │
│  ────────────────        │
│                          │
│  Question Type           │
│  [Checkbox List]         │
│                          │
│  ────────────────        │
│                          │
│  Marks                   │
│  [Range Slider]          │
│                          │
│  [Apply Filters]         │
│                          │
└──────────────────────────┘
```

**Section Header**:
- Typography: H4 (16px), Weight 600, Slate-900
- Layout: Flex, space-between
- Margin-bottom: 16px

**Clear All Link**:
- Typography: 13px, Weight 500, Indigo-600
- Hover: Indigo-700, underline

**Filter Group**:
- Margin-bottom: 24px
- Padding-bottom: 24px
- Border-bottom: 1px Slate-200 (except last)

**Group Label**:
- Typography: 14px, Weight 600, Slate-700
- Margin-bottom: 12px

**Checkbox Item**:
- Size: 40px height
- Layout: Flex row, align-center
- Gap: 10px
- Hover: Background Slate-50
- Border-radius: 6px
- Padding: 8px

*Checkbox*:
- Size: 18x18px
- Border: 2px Slate-300
- Border-radius: 4px
- Checked: Indigo-600 bg, White checkmark

*Label*:
- Typography: 14px, Slate-700
- Flex: 1

*Count Badge*:
- Typography: 12px, Weight 500, Slate-500
- Background: Slate-100
- Padding: 2px 8px
- Border-radius: 999px

**Range Slider** (Year, Marks):
- Track height: 4px
- Track color: Slate-200
- Fill color: Indigo-600
- Thumb: 16x16px circle, White with shadow
- Labels: Above and below slider
- Typography: 13px, Slate-600

**Example Subjects**:
- ☑ Data Structures (245)
- ☐ Algorithms (189)
- ☐ Operating Systems (156)
- ☐ Database Management (198)
- ☐ Computer Networks (134)
- ... (show more)

**Radio Group** (Difficulty):
```
○ All Difficulties
○ Easy
○ Medium
● Hard
```

- Size: 36px height per option
- Radio: 16x16px circle
- Selected: Indigo-600 fill
- Typography: 14px, Slate-700

**Apply Button** (Bottom):
- Size: 44px height, full width
- Background: Indigo-600
- Text: White, 15px, Weight 600
- Border-radius: 8px
- Sticky bottom of sidebar
- Shadow: lg

#### Results Area
**Flex**: 1 (takes remaining space)
**Min-width**: 0 (prevent overflow)

**Results Header**:
```
┌──────────────────────────────────────────────────────┐
│  Showing 1,234 results for "binary tree"            │
│                                                       │
│  Sort by: [Relevance ▼] [Best Match ▼]              │
│                                          [Grid] [List]│
└──────────────────────────────────────────────────────┘
```

**Background**: White
**Padding**: 20px 24px
**Border-radius**: 12px 12px 0 0
**Border-bottom**: 1px Slate-200

**Results Text**:
- Typography: 16px, Slate-900
- Query highlight: Indigo-600, Weight 600

**Sort Dropdowns**:
- Size: 36px height
- Gap: 12px
- Border: 1px Slate-300
- Border-radius: 6px
- Typography: 14px, Slate-700
- Icon: Chevron down

**View Toggle**:
- Two icon buttons
- Size: 36x36px
- Border: 1px Slate-300
- Active: Indigo-600 bg, White icon
- Gap: 4px between buttons

**Results List** (Default View):
```
┌────────────────────────────────────────────────────┐
│  [Question Card 1]                                 │
├────────────────────────────────────────────────────┤
│  [Question Card 2]                                 │
├────────────────────────────────────────────────────┤
│  [Question Card 3]                                 │
└────────────────────────────────────────────────────┘
```

**Container**:
- Background: White
- Border-radius: 0 0 12px 12px

**Question Result Card**:
```
┌──────────────────────────────────────────────────────┐
│  [Score: 95%]                                  [•••] │
│                                                       │
│  Explain the concept of binary search tree and       │
│  demonstrate how to insert and delete nodes. What    │
│  is the time complexity of these operations?         │
│                                                       │
│  📚 Data Structures • 📅 2023 • ⭐ Medium • 10 marks│
│  📄 exam_2023_final.pdf (Page 5, Q7)                │
│                                                       │
│  [View Details] [Add to Collection] [Similar (12)]   │
└──────────────────────────────────────────────────────┘
```

**Card Styling**:
- Padding: 24px
- Border-bottom: 1px Slate-200
- Hover: Background Slate-50, border-left 4px Indigo-500
- Transition: All 0.2s

**Relevance Score**:
- Position: Top-right
- Typography: 13px, Weight 600
- Background: Emerald-100
- Color: Emerald-700
- Padding: 4px 10px
- Border-radius: 999px

**Question Text**:
- Typography: 16px, Line-height 1.6, Slate-900
- Max-height: 4.8em (3 lines)
- Overflow: Show more link
- Search term highlighting: Yellow background, Weight 600

**Metadata Row**:
- Layout: Flex row wrap, gap 16px
- Typography: 13px, Slate-600
- Margin-top: 16px
- Icons: 14x14px

**Source Info**:
- Typography: 12px, Slate-500
- Font: JetBrains Mono (for file name)
- Margin-top: 8px

**Action Buttons**:
- Layout: Flex row, gap 12px
- Size: 32px height
- Variant: Ghost
- Typography: 13px, Weight 500
- Margin-top: 16px

**Grid View** (Alternative):
**Layout**: Grid 2 columns (desktop), 1 column (tablet/mobile)
**Gap**: 20px

```
┌─────────────────┬─────────────────┐
│  [Card]         │  [Card]         │
│                 │                 │
├─────────────────┼─────────────────┤
│  [Card]         │  [Card]         │
│                 │                 │
└─────────────────┴─────────────────┘
```

**Grid Card** (Compact):
- Aspect: Auto height
- Padding: 20px
- Background: White
- Border: 1px Slate-200
- Border-radius: 10px
- Hover: Shadow-md, translate-y -2px

**Pagination** (Bottom):
```
┌──────────────────────────────────────────────────────┐
│    [← Previous]  [1] [2] [3] ... [47]  [Next →]     │
└──────────────────────────────────────────────────────┘
```

**Container**:
- Padding: 32px
- Layout: Flex row, center, gap 8px

**Page Button**:
- Size: 40x40px
- Border-radius: 6px
- Typography: 14px, Weight 500
- Default: Slate-700, hover Slate-100
- Active: Indigo-600 bg, White text

**Empty State** (No Results):
```
┌────────────────────────────────────────┐
│                                         │
│         [Search Icon - Large]           │
│                                         │
│     No questions found for              │
│       "quantum mechanics"               │
│                                         │
│  Try adjusting your filters or          │
│  search with different keywords         │
│                                         │
│  [Clear Filters] [Try Suggestions]      │
│                                         │
└────────────────────────────────────────┘
```

- Height: 500px
- Background: White
- Border-radius: 12px
- Padding: 60px
- Text: Center aligned, Slate-600

---

### 5. Question Detail Page
**Route**: `/questions/:questionId`
**Purpose**: Full question view with context and similar questions

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│                    Navigation Bar                         │
├─────────────────────────────────────────────────────────┤
│ [← Back to Results]                                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────┬────────────────────────┐  │
│  │                          │                        │  │
│  │   Question Details       │    Sidebar:           │  │
│  │   (Full Content)         │    - Metadata         │  │
│  │                          │    - Actions          │  │
│  │                          │    - Source Info      │  │
│  │                          │                        │  │
│  └──────────────────────────┴────────────────────────┘  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Similar Questions                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Page Container
**Background**: Slate-50
**Padding**: 40px horizontal, 32px top

**Back Button**:
- Icon: Arrow left
- Text: "Back to Results"
- Variant: Ghost
- Margin-bottom: 24px

#### Main Content Grid
**Layout**: 2 columns (2fr 1fr ratio)
**Gap**: 32px
**Max-width**: 1400px

#### Left Column - Question Content

**Question Card**:
```
┌──────────────────────────────────────────────────┐
│  Question 7                      [Bookmark] [⋯]  │
│                                                   │
│  [Full Question Text]                            │
│                                                   │
│  Explain the concept of binary search tree       │
│  and demonstrate the following operations:       │
│                                                   │
│  a) Insertion of nodes                           │
│  b) Deletion of nodes                            │
│  c) Searching for a value                        │
│                                                   │
│  Also analyze the time complexity for each       │
│  operation in best, average, and worst cases.    │
│  Provide examples with diagrams.                 │
│                                                   │
│  ──────────────────────────────────              │
│                                                   │
│  📝 Answer Guidelines (if available)             │
│  [Expandable section with marking scheme]        │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Card Styling**:
- Background: White
- Border: 1px Slate-200
- Border-radius: 12px
- Padding: 32px
- Shadow: sm

**Question Number Badge**:
- Typography: 14px, Weight 600, Slate-600
- Background: Slate-100
- Padding: 6px 12px
- Border-radius: 6px

**Actions** (Top-right):
- Bookmark button: Heart/star icon
- More menu: Three dots

**Question Text**:
- Typography: 18px, Line-height 1.8, Slate-900
- Whitespace: Preserved (for formatting)
- Margin-top: 24px

**Sub-questions** (a, b, c):
- Typography: 17px, Slate-800
- Padding-left: 32px
- Margin: 12px vertical
- List-style: Lower-alpha

**Answer Guidelines Section**:
- Margin-top: 32px
- Border-top: 1px Slate-200
- Padding-top: 24px

*Header*:
- Typography: 16px, Weight 600, Slate-900
- Icon: Document with checkmark
- Expandable accordion

*Content* (Expanded):
- Background: Indigo-50
- Padding: 20px
- Border-radius: 8px
- Typography: 15px, Slate-700
- Line-height: 1.6

**Context Section** (Below main card):
**Margin-top**: 24px

```
┌──────────────────────────────────────────────────┐
│  📄 Source Context                                │
│                                                   │
│  From: exam_2023_final.pdf                       │
│  Page: 5                                          │
│  Position: Question 7 of 10                      │
│                                                   │
│  [View Full Page] [Download PDF]                 │
│                                                   │
│  ──────────────────────────────────              │
│                                                   │
│  Related Questions in this Paper:                │
│  → Q4: Implement AVL tree rotation               │
│  → Q9: Compare BST with other data structures    │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Same white card styling**
**Padding**: 24px

**Links**:
- Typography: 14px, Indigo-600, Weight 500
- Hover: Indigo-700, underline
- Icon: Arrow right

#### Right Sidebar - Metadata & Actions

**Info Card**:
```
┌─────────────────────────────┐
│  Metadata                   │
│                             │
│  📚 Subject                 │
│  Data Structures            │
│                             │
│  📅 Year                    │
│  2023                       │
│                             │
│  📝 Exam Type               │
│  Final Examination          │
│                             │
│  ⭐ Difficulty              │
│  Medium                     │
│                             │
│  📊 Marks                   │
│  10 marks                   │
│                             │
│  🏷️ Tags                    │
│  [BST] [Trees]              │
│  [Algorithms]               │
│                             │
│  ─────────────────          │
│                             │
│  📈 Statistics              │
│                             │
│  Searched: 47 times         │
│  Saved: 12 times            │
│  Similar: 15 questions      │
│                             │
└─────────────────────────────┘
```

**Card Styling**: Same as left column
**Width**: 100% of sidebar
**Position**: Sticky top

**Metadata Row**:
- Layout: Key-value pairs
- Gap: 16px vertical
- Key: Icon + label (13px, Slate-600)
- Value: 14px, Weight 600, Slate-900

**Tags**:
- Display: Flex wrap, gap 8px
- Chip styling:
  - Size: 28px height
  - Padding: 4px 10px
  - Background: Indigo-100
  - Color: Indigo-700
  - Border-radius: 999px
  - Typography: 12px, Weight 500

**Statistics Section**:
- Border-top: 1px Slate-200
- Padding-top: 20px
- Margin-top: 20px
- Typography: 13px, Slate-600

**Actions Card**:
**Margin-top**: 20px

```
┌─────────────────────────────┐
│  Actions                    │
│                             │
│  [📥 Add to Collection]    │
│                             │
│  [🔗 Copy Link]            │
│                             │
│  [📤 Share Question]       │
│                             │
│  [🖨️ Print/Export]         │
│                             │
│  [⚠️ Report Issue]         │
│                             │
└─────────────────────────────┘
```

**Action Button** (Full width):
- Size: 44px height
- Padding: 12px 16px
- Background: Slate-50
- Border: 1px Slate-200
- Border-radius: 8px
- Typography: 14px, Weight 500, Slate-700
- Layout: Icon left, text center-left
- Gap: 12px
- Margin-bottom: 12px
- Hover: Slate-100,radius: 12px
- Padding: 24px
- Shadow: sm
- Hover: shadow-md

**Status Badge** (Top-right):
- Size: Auto width, 28px height
- Padding: 4px 12px
- Border-radius: 999px
- Typography: 12px, Weight 600, Uppercase

Colors by status:
- Queued: Purple-100 bg, Purple-700 text
- Processing: Blue-100 bg, Blue-700 text
- Completed: Emerald-100 bg, Emerald-700 text
- Failed: Red-100 bg, Red-700 text

**Job ID**:
- Typography: 14px, Weight 500, Slate-500
- Font: JetBrains Mono (monospace)
- Copy button on hover

**File List**:
- Same styling as upload zone file items
- Collapsed if more than 3 files (show count)
- Expandable accordion

**Progress Section**:
- Progress Bar: Full width, 12px height
- Percentage: 16px, Weight 600, Slate-900
- Background gradient for active processing

**Status Text**:
- Typography: 14px, Slate-600
- Margin-top: 12px

**Timestamp**:
- Typography: 12px, Slate-400
- Relative time (e.g., "2 minutes ago")

**Action Buttons**:
- Layout: Flex row, 12px gap
- "View Details": Ghost variant
- "Cancel Job": Ghost variant, Red on hover (only for active jobs)

#### Empty State (No Jobs)
```
┌────────────────────────────────────────┐
│                                         │
│         [Illustration/Icon]             │
│                                         │
│      No upload jobs yet                 │
│                                         │
│  Upload your first question papers      │
│     to get started                      │
│                                         │
└────────────────────────────────────────┘
```

- Height: 400px
- Background: White
- Border: 1px dashed Slate-300
- Border-radius: 12px
- Text: Slate-500, centered

---

### 3. Job Details Page
**Route**: `/jobs/:jobId`
**Purpose**: Detailed view of single job with full processing logs

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│                    Navigation Bar                         │
├─────────────────────────────────────────────────────────┤
│ [← Back to Jobs]                                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────┬────────────────────────────────┐   │
│  │                │                                 │   │
│  │   Job Info     │    Processing Timeline         │   │
│  │   Card         │                                 │   │
│  │                │                                 │   │
│  ├────────────────┤                                 │   │
│  │                │                                 │   │
│  │  Files List    │                                 │   │
│  │                │                                 │   │
│  └────────────────┴────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Extracted Questions Preview             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Page Header
**Padding**: 40px horizontal, 32px vertical
**Background**: Slate-50

*Back Button*:
- Icon: Arrow left
- Text: "Back to Jobs"
- Variant: Ghost
- Hover: Slate-100

*Title Section*:
- Margin-top: 24px
- Layout: Flex row, space-between, align-center

```
[Job ID: abc-123-def]    [Status Badge] [Actions Menu]
```

**Job ID Display**:
- Typography: H2 (30px), Weight 700
- Font: JetBrains Mono
- Color: Slate-900
- Copy button inline

**Status Badge**: Same as job card, larger (36px height)

**Actions Dropdown**:
- Icon: Three dots vertical
- Menu options:
  - "Reprocess Job" (if failed)
  - "Export Results"
  - "Download Files"
  - "Delete Job"

#### Main Content Grid
**Layout**: 2 columns (1fr 2fr ratio)
**Gap**: 32px
**Padding**: 40px horizontal, 0px vertical

#### Left Column - Job Information

**Job Info Card**:
```
┌────────────────────────────────┐
│  Job Information               │
│                                │
│  Status: [Badge]               │
│  Created: Jan 15, 2025 2:30PM │
│  Duration: 2m 34s              │
│  Progress: 100%                │
│                                │
│  ─────────────────────         │
│                                │
│  📊 Results                    │
│                                │
│  Total Questions: 245          │
│  Files Processed: 3            │
│  Pages Scanned: 87             │
│  Errors: 0                     │
│                                │
└────────────────────────────────┘
```

**Card Styling**:
- Background: White
- Border: 1px Slate-200
- Border-