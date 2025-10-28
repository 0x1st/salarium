# Style Alignment Guide: Statistics to Information Management

This document outlines the visual alignment between the **Statistics (统计分析)** section and the **Information Management (信息管理)** section.

## Overview

All visual styles in the Statistics section have been aligned to match the Information Management section, ensuring a consistent user experience across the entire application.

## Design Tokens

### Colors

#### Text Colors
- **Primary Text**: `#2c3e50` (Main headings, body text, table cells)
- **Secondary Text**: `#7f8c8d` (Subtitles, labels, helper text)
- **Tertiary Text**: `#909399` (Less important text)
- **Light Text**: `#6b7280` (Placeholder text)

#### Background Colors
- **Page Background**: `linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)`
- **Card Background**: `#ffffff`
- **Table Header**: `#f9fafb`

#### Border Colors
- **Default Border**: `#e2e8f0`
- **Hover Border**: `#cbd5e1`

#### Gradient Colors (for titles and stat cards)
- **Primary Gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Blue Gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Green Gradient**: `linear-gradient(135deg, #f093fb 0%, #f5576c 100%)`
- **Orange Gradient**: `linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)`
- **Purple Gradient**: `linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)`

### Typography

#### Font Sizes
- **H1**: 32px
- **H2 (Page Title)**: 28px, font-weight: 700
- **H3**: 24px
- **Page Subtitle**: 16px
- **Card Title**: 18px, font-weight: 600
- **Body Text**: 14px
- **Stat Label**: 14px, font-weight: 500
- **Stat Value**: 24px, font-weight: 700 (for stat cards)

#### Line Heights
- **Base**: 1.6
- **Headings**: 1.2-1.4

### Shadows

- **Card Shadow**: `0 8px 32px rgba(0, 0, 0, 0.1)`
- **Card Hover Shadow**: `0 12px 40px rgba(0, 0, 0, 0.15)`
- **Button Hover Shadow**: `0 4px 12px rgba(64, 158, 255, 0.3)`

### Border Radius

- **Small**: 8px (buttons, inputs)
- **Medium**: 12px
- **Large**: 16px (cards)

### Spacing

- **Container Padding**: 24px
- **Card Padding**: 20-24px
- **Card Gap**: 20px
- **Section Gap**: 32px
- **Toolbar Gap**: 12px

## Component Alignment

### Page Headers

All statistics pages now use:
```scss
.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}
```

### Cards (el-card)

All cards now have consistent styling:
```css
.el-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: none;
}

.el-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
```

### Stat Cards / KPI Cards

Stat cards now use the same visual pattern as Information Management:
- White background
- Gradient top border (4px height)
- Icon + value + label layout
- Shadow: `0 4px 16px rgba(0, 0, 0, 0.08)`
- Hover effect: `translateY(-2px)` + shadow increase

### Tables

Tables maintain consistent styling:
- Header background: `#f9fafb`
- Header text: `#2c3e50`, font-weight: 600
- Body text: `#2c3e50`
- Border color: `#e2e8f0`
- Cell padding: 12-16px

### Buttons

Buttons have consistent interactions:
- Border radius: 8px
- Font weight: 500
- Hover effect for primary buttons: `translateY(-1px)` + shadow

### Form Controls

All form controls (inputs, selects) use:
- Border radius: 8px
- Text color: `#2c3e50`
- Font size: 14px
- Border color: `#e2e8f0`
- No focus box-shadow (clean minimal design)

## Files Modified

### New Files Created
1. `/frontend/src/styles/theme.scss` - Design token variables
2. `/frontend/src/styles/element-plus-overrides.scss` - SCSS version of overrides (for future use)

### Modified Files

#### Statistics Views
1. `/frontend/src/views/stats/Index.vue`
   - Updated page title to use gradient text
   - Updated background gradient
   - Updated subtitle color
   - Increased title font size to 28px

2. `/frontend/src/views/stats/Net.vue`
   - Added consistent card shadows and hover effects
   - Updated gap spacing to 20px

3. `/frontend/src/views/stats/Composition.vue`
   - Added consistent card shadows and hover effects
   - Updated gap spacing to 20px

4. `/frontend/src/views/stats/Deductions.vue`
   - Added consistent card styling

5. `/frontend/src/views/stats/Cumulative.vue`
   - Added consistent card styling

6. `/frontend/src/views/stats/Table.vue`
   - Added consistent card styling
   - Updated action bar spacing

#### Components
1. `/frontend/src/components/stats/KPICards.vue`
   - Complete redesign to match Information Management stat cards
   - Added gradient top borders
   - Added icons
   - Updated layout and typography

2. `/frontend/src/components/stats/ChartCard.vue`
   - Updated text colors to `#2c3e50`
   - Updated secondary text to `#7f8c8d`
   - Improved font sizes and spacing

#### Global Styles
1. `/frontend/src/assets/element-plus-overrides.css`
   - Added comprehensive card styling
   - Updated table colors to match
   - Added button hover effects
   - Updated form control styling
   - Updated empty state colors
   - Added consistent border radius values

## Verification Checklist

- [x] Page titles use gradient text effect
- [x] Cards have consistent 16px border radius
- [x] Cards have consistent shadows (0 8px 32px rgba(0, 0, 0, 0.1))
- [x] Card hover effects are consistent (translateY + shadow increase)
- [x] Typography uses correct colors (#2c3e50 for primary, #7f8c8d for secondary)
- [x] Spacing is consistent (20-24px gaps)
- [x] Buttons have hover effects
- [x] Form controls have consistent styling
- [x] Tables use aligned colors
- [x] Empty states use correct typography
- [x] Background gradient matches Information Management

## Theme Variables Location

All theme variables are centralized in:
- `/frontend/src/styles/theme.scss` (SCSS variables and mixins)
- `/frontend/src/assets/element-plus-overrides.css` (Applied CSS overrides)

## Usage Guidelines

### For New Components

When creating new components in the statistics section:

1. Use the established color palette (refer to Design Tokens)
2. Apply card styles using `.el-card` or import from theme.scss
3. Use consistent spacing values (20px, 24px, 32px)
4. Apply gradient text to main titles using the mixin or CSS class
5. Ensure hover states follow the pattern (translateY + shadow)

### For Text Elements

- Primary text: Use `#2c3e50`
- Secondary text: Use `#7f8c8d`
- Card titles: 18px, font-weight: 600, color: #2c3e50
- Page titles: 28px, font-weight: 700, with gradient effect

### For Cards

Always use:
```vue
<el-card shadow="hover">
  <!-- content -->
</el-card>
```

The global styles will handle the rest.

## Migration Notes

No breaking changes were introduced. All modifications are purely visual enhancements that maintain backward compatibility with existing functionality.

## Browser Compatibility

All CSS features used are widely supported:
- CSS gradients
- CSS transforms
- CSS transitions
- Box shadows
- Border radius

Tested on: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
