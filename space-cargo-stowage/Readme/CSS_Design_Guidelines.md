# Space Cargo Stowage - CSS Design Guidelines & Naming Conventions

## 📋 Table of Contents
1. [Design System Architecture](#design-system-architecture)
2. [CSS Naming Conventions](#css-naming-conventions)
3. [File Structure](#file-structure)
4. [Component Design Patterns](#component-design-patterns)
5. [Best Practices](#best-practices)
6. [Common Patterns Reference](#common-patterns-reference)

---

## 🏗️ Design System Architecture

### Three-Tier CSS Architecture
```
styles1.css (Foundation Layer)
├── CSS Custom Properties (Colors, Spacing, Typography)
├── Global Resets & Base Styles
├── Utility Classes (.flex, .grid, .text-center)
└── Responsive Breakpoints

components1.css (Shared Component Layer)
├── Reusable Component Patterns (.card, .btn, .grid-container)
├── Layout Systems (.grid-2x2, .grid-2x1, .grid-single)
├── Form Elements (.input-field, .select-field)
└── Loading States & Data Tables

[component]1.css (Component-Specific Layer)
├── Page-specific layouts
├── Unique component behaviors
└── Component-specific overrides
```

---

## 🎯 CSS Naming Conventions

### Core Principles
1. **Use multiple classes instead of overly specific single classes**
2. **Combine generic classes with specific IDs**
3. **Follow BEM-inspired but simplified methodology**
4. **Prioritize reusability and maintainability**

### Class Naming Patterns

#### 📦 Layout Classes (Generic & Reusable)
```css
/* Container Types */
.main-container    /* Primary page container */
.content-container /* Content wrapper */
.section-container /* Section wrapper */

/* Grid Systems */
.grid-container    /* Base grid container */
.grid-2x2         /* 2x2 grid layout */
.grid-2x1         /* 2x1 grid layout */
.grid-single      /* Single column layout */
.grid-responsive  /* Auto-responsive grid */

/* Layout Boxes */
.grid-box         /* Generic grid item */
.content-box      /* Content container box */
.card             /* Card component */
.panel            /* Side panel */
```

#### 🎨 Component Classes (Functional)
```css
/* Buttons */
.btn              /* Base button */
.btn-primary      /* Primary action button */
.btn-secondary    /* Secondary action button */
.btn-upload       /* File upload button */
.btn-large        /* Large button variant */

/* Form Elements */
.input-field      /* Generic input styling */
.select-field     /* Select dropdown styling */
.file-input       /* File input styling */
.search-input     /* Search-specific input */

/* Data Display */
.data-table       /* Table component */
.status-badge     /* Status indicator */
.progress-bar     /* Progress indicator */
.stat-card        /* Statistics card */

/* Interactive Elements */
.upload-zone      /* File upload area */
.loading-screen   /* Loading state */
.error-message    /* Error display */
.success-message  /* Success display */
```

#### 🏷️ State & Modifier Classes
```css
/* States */
.is-active        /* Active state */
.is-loading       /* Loading state */
.is-disabled      /* Disabled state */
.is-hidden        /* Hidden element */
.is-visible       /* Visible element */

/* Variants */
.variant-success  /* Success variant */
.variant-warning  /* Warning variant */
.variant-error    /* Error variant */
.variant-info     /* Info variant */

/* Sizes */
.size-small       /* Small variant */
.size-medium      /* Medium variant (default) */
.size-large       /* Large variant */
.size-full        /* Full width/height */
```

### ID Naming Patterns

#### 🆔 Use IDs for Unique Elements
```css
/* Page Identifiers */
#dashboard-page
#items-page
#containers-page
#search-page

/* Unique Sections */
#main-navigation
#user-profile-section
#file-upload-area
#stats-overview

/* Form Elements */
#items-csv-upload
#containers-csv-upload
#search-input-field
#date-range-picker
```

### Multiple Class Example
```html
<!-- ❌ Bad: Overly specific single class -->
<div class="dashboard-main-container-with-grid-layout">

<!-- ✅ Good: Multiple descriptive classes -->
<div class="main-container grid-container grid-2x2" id="dashboard-page">
  <div class="grid-box content-box" id="dashboard-stats">
  <div class="grid-box upload-zone" id="file-upload-section">
</div>
```

---

## 📁 File Structure

### CSS Files Organization
```
src/styles/
├── styles1.css           # Foundation (variables, resets, utilities)
├── components1.css       # Shared components (buttons, forms, grids)
├── dashboard1.css        # Dashboard-specific styles
├── items1.css           # Items page styles
├── containers1.css      # Containers page styles
├── search1.css          # Search page styles
├── wastage1.css         # Wastage page styles
├── systemlogs1.css      # System logs styles
├── simulation1.css      # Simulation styles
├── header1.css          # Header component styles
├── sidebar1.css         # Sidebar component styles
└── parts1.css           # Button components styles
```

### Import Order (Critical!)
```css
/* In App.jsx - Foundation files MUST come first */
import "./styles/styles1.css";        /* 1. Foundation layer */
import "./styles/components1.css";    /* 2. Shared components */
/* Component-specific CSS imports in individual components */
```

---

## 🧩 Component Design Patterns

### Standard Page Layout Pattern
```html
<div class="main-container grid-container" id="[page-name]-page">
  <!-- Grid layout specific to page needs -->
  <div class="grid-box content-box" id="[section-name]">
    <h2 class="section-title">[Section Name]</h2>
    <div class="section-content">
      <!-- Content here -->
    </div>
  </div>
</div>
```

### Upload Section Pattern
```html
<div class="grid-box upload-zone" id="file-upload-section">
  <h2 class="section-title">Import Data</h2>
  <div class="upload-area">
    <input type="file" class="file-input" id="csv-upload">
    <label for="csv-upload" class="btn btn-secondary">Choose File</label>
    <button class="btn btn-primary btn-upload">Upload</button>
  </div>
</div>
```

### Data Display Pattern
```html
<div class="grid-box content-box" id="data-display-section">
  <h2 class="section-title">Data Overview</h2>
  <div class="data-container">
    <div class="data-table-container">
      <table class="data-table">
        <!-- Table content -->
      </table>
    </div>
  </div>
</div>
```

### Stats/Cards Pattern
```html
<div class="grid-box stats-container" id="stats-overview">
  <h2 class="section-title">Statistics</h2>
  <div class="stats-grid">
    <div class="stat-card">
      <span class="stat-value">150</span>
      <span class="stat-label">Total Items</span>
    </div>
  </div>
</div>
```

---

## ✅ Best Practices

### CSS Writing Guidelines

1. **Use CSS Custom Properties**
   ```css
   /* ✅ Use variables from styles1.css */
   .btn-primary {
     background: var(--primary);
     color: var(--white);
     padding: var(--space-3) var(--space-6);
   }
   ```

2. **Mobile-First Responsive Design**
   ```css
   /* ✅ Start with mobile, enhance for larger screens */
   .grid-container {
     grid-template-columns: 1fr;
   }
   
   @media (min-width: 768px) {
     .grid-container {
       grid-template-columns: 1fr 1fr;
     }
   }
   ```

3. **Consistent Spacing**
   ```css
   /* ✅ Use consistent spacing variables */
   .section-content {
     padding: var(--space-6);
     margin-bottom: var(--space-4);
     gap: var(--space-3);
   }
   ```

4. **Glassmorphism Effect Usage**
   ```css
   /* ✅ Use predefined glass effects */
   .content-box {
     background: var(--glass-bg);
     backdrop-filter: var(--glass-backdrop);
     border: var(--glass-border);
     box-shadow: var(--glass-shadow);
   }
   ```

### Component Development Guidelines

1. **Always use multiple classes**
2. **Use IDs for unique elements only**
3. **Leverage utility classes from styles1.css**
4. **Follow the three-tier import structure**
5. **Test responsiveness on mobile, tablet, desktop**

---

## 📚 Common Patterns Reference

### Grid Layouts
```css
/* Dashboard: 2x2 Grid */
.grid-2x2 {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 0.8fr 1.2fr;
}

/* Search: 2x1 Grid */
.grid-2x1 {
  grid-template-columns: 1.3fr 0.7fr;
  grid-template-rows: 1fr;
}

/* System Logs: Single Column */
.grid-single {
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr;
}
```

### Button Combinations
```html
<!-- Standard Action Button -->
<button class="btn btn-primary">Save Changes</button>

<!-- Upload Button -->
<button class="btn btn-upload btn-large">Upload File</button>

<!-- Secondary Action -->
<button class="btn btn-secondary size-small">Cancel</button>

<!-- Success State -->
<button class="btn btn-primary variant-success">Complete</button>
```

### Loading States
```html
<!-- Full Page Loading -->
<div class="loading-screen" id="page-loader">
  <div class="loading-spinner"></div>
  <p class="loading-text">Loading data...</p>
</div>

<!-- Section Loading -->
<div class="content-box is-loading" id="data-section">
  <div class="partial-loader">Loading...</div>
</div>
```

---

## 🔄 Migration Strategy

### Current State → Target State

#### Before (Current)
```html
<div class="dashboard-container">
  <div class="grid-box left-panel">
```

#### After (Target)
```html
<div class="main-container grid-container grid-2x2" id="dashboard-page">
  <div class="grid-box content-box panel-main" id="main-content-area">
```

### Implementation Steps
1. ✅ Create design guidelines (this file)
2. 🔄 Update component class names systematically
3. 🔄 Test each component after update
4. 🔄 Ensure responsive behavior
5. 🔄 Validate accessibility
6. 🔄 Document any custom patterns

---

## 🎨 Color Scheme & Design Tokens

### Current Theme: Deep Teal Professional
- **Primary**: `#0f766e` (Deep professional teal)
- **Primary Light**: `#14b8a6` (Hover states)
- **Primary Dark**: `#134e4a` (Pressed states)
- **Success**: `#10b981` (Success states)
- **Warning**: `#f59e0b` (Warning states)
- **Error**: `#ef4444` (Error states)

### Typography
- **Font Family**: Inter (professional, modern)
- **Sizes**: `--text-xs` to `--text-4xl`
- **Weights**: normal(400), medium(500), semibold(600), bold(700)

---

## 🚀 Future Enhancements

### Potential Improvements
1. **CSS-in-JS Integration** (styled-components, emotion)
2. **CSS Modules** for better encapsulation
3. **Sass/SCSS** for advanced features
4. **PostCSS** for optimization
5. **Design System Package** for reusability across projects

### Performance Considerations
1. **Critical CSS** inlining
2. **CSS purging** for production
3. **Component lazy loading**
4. **Asset optimization**

---

*Last Updated: June 8, 2025*
*Version: 1.0*
*Project: Space Cargo Stowage Management System*
