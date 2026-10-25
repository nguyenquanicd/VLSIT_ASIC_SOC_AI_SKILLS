# Shape sizing guide

Reference only. `rule.md` (RHD-051, RHD-052) takes precedence. The estimates below are for 18 pt text in the default draw.io font (Helvetica); check the rendered preview when available and adjust.

## Text box estimate

- Line height: about 22 px.
- Character width: about 9 px on average for lower-case text and digits (about 11 px for upper case, 5-6 px for narrow characters such as `i`, `l`, `t`). Use 9 px per character when checking the RHD-052 fill ratios, and 10 px per character when reserving space for labels (conservative).
- Text width = longest line characters x 9 px (check) or x 10 px (reserve). Text height = number of lines x 22 px.

## Shape size from the text box (w_t x h_t)

| Shape | Width | Height |
|---|---|---|
| Rectangle | w_t + 2 x 12 px (range w_t + 16 to w_t + 40) | h_t + 2 x 12 px (range h_t + 16 to h_t + 40) |
| Square | max(w_t, h_t) + 24 px | same as width |
| Circle / ellipse | diameter = max(w_t / 0.7, h_t / 0.7), not above 1.6 x sqrt(w_t^2 + h_t^2) | same for a circle |

Worked example: label `u_fifo` / `(axis_downscaler_fifo)`: longest line 21 characters, so w_t = 189 px (at 9 px per character) and h_t = 44 px. Rectangle about 213 x 68 px. Fill ratios: 189/213 = 89% width, 44/68 = 65% height, both within RHD-052.

## Checklist before delivery

1. For each shape, compute text-box fill ratios and compare with RHD-052.
2. Shapes that fail are resized, never fixed by changing the font size.
3. Shapes with similar labels share one size (use the largest required size within the group if needed).
