#pragma once

#include <cmath>

#include <array>
#include <iostream>
#include <optional>

namespace dm {

template <typename T>
class Vec2
{
  public:
    using dimension_type = T;

    constexpr Vec2() : Vec2{0, 0} {}
    constexpr Vec2(T x, T y) : elements_{x, y} {}
    constexpr Vec2(std::initializer_list<T> list)
    {
        std::copy(list.begin(), list.end(), elements_.begin());
    }

    [[nodiscard]] static constexpr Vec2<T> unit_x() noexcept
    {
        return {1, 0};
    }

    [[nodiscard]] static constexpr Vec2<T> unit_y() noexcept
    {
        return {0, 1};
    }

    [[nodiscard]] constexpr std::array<T, 2> elements() const noexcept
    {
        return elements_;
    }

    [[nodiscard]] constexpr std::array<T, 2>& elements() noexcept
    {
        return elements_;
    }

    [[nodiscard]] constexpr T x() const noexcept
    {
        return elements_[x_axis];
    }

    [[nodiscard]] constexpr T& x() noexcept
    {
        return elements_[x_axis];
    }

    [[nodiscard]] constexpr T y() const noexcept
    {
        return elements_[y_axis];
    }

    [[nodiscard]] constexpr T& y() noexcept
    {
        return elements_[y_axis];
    }

    [[nodiscard]] friend constexpr Vec2<T> operator-(const Vec2<T>& value) noexcept
    {
        return {-value.x(), -value.y()};
    }

    [[nodiscard]] friend constexpr Vec2<T> operator-(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return {lhs.x() - rhs.x(), lhs.y() - rhs.y()};
    }

    [[nodiscard]] friend constexpr Vec2<T> operator+(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return {lhs.x() + rhs.x(), lhs.y() + rhs.y()};
    }

    template <typename U>
    [[nodiscard]] friend constexpr Vec2<T> operator*(U n, const Vec2<T>& value) noexcept
    {
        return {n * value.x(), n * value.y()};
    }

    template <typename U>
    [[nodiscard]] friend constexpr Vec2<T> operator*(const Vec2<T>& value, U n) noexcept
    {
        return n * value;
    }

    template <typename U>
    [[nodiscard]] friend constexpr Vec2<T> operator/(const Vec2<T>& value, U n) noexcept
    {
        return {value.x() / n, value.y() / n};
    }

    constexpr Vec2<T>& operator-=(const Vec2<T>& other) noexcept
    {
        return *this = *this - other;
    }

    constexpr Vec2<T>& operator+=(const Vec2<T>& other) noexcept
    {
        return *this = *this + other;
    }

    constexpr Vec2<T>& operator*=(T n) noexcept
    {
        return *this = *this * n;
    }

    constexpr Vec2<T>& operator/=(T n) noexcept
    {
        return *this = *this / n;
    }

    [[nodiscard]] constexpr T magnitude_squared() const noexcept
    {
        return x() * x() + y() * y();
    }

    [[nodiscard]] constexpr double magnitude() const noexcept
    {
        return std::sqrt(magnitude_squared());
    }

    constexpr Vec2<T>& normalize() noexcept
    {
        return *this /= magnitude();
    }

    [[nodiscard]] friend constexpr bool operator==(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return lhs.x() == rhs.x() && lhs.y() == rhs.y();
    }

    [[nodiscard]] friend constexpr bool operator!=(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return !(lhs == rhs);
    }

    [[nodiscard]] friend constexpr bool operator<(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return (lhs.x() != rhs.x()) ? lhs.x() < rhs.x() : lhs.y() < rhs.y();
    }

    [[nodiscard]] friend constexpr bool operator>(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return rhs < lhs;
    }

    [[nodiscard]] friend constexpr bool operator<=(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return !(lhs > rhs);
    }

    [[nodiscard]] friend constexpr bool operator>=(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return !(lhs < rhs);
    }

    [[nodiscard]] static constexpr T distance_squared(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        Vec2<T> delta = abs_difference(lhs, rhs);
        return delta.x() * delta.x() + delta.y() * delta.y();
    }

    [[nodiscard]] static constexpr T distance(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return std::sqrt(distance_squared(lhs, rhs));
    }

    [[nodiscard]] static constexpr T chebyshev_distance(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        Vec2<T> delta = abs_difference(lhs, rhs);
        return std::max(delta.x(), delta.y());
    }

    [[nodiscard]] static constexpr T manhattan_distance(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        Vec2<T> delta = abs_difference(lhs, rhs);
        return delta.x() + delta.y();
    }

    friend std::ostream& operator<<(std::ostream& output, const Vec2<T>& value)
    {
        return output << "{" << value.x() << ", " << value.y() << "}";
    }

  private:
    static constexpr std::size_t x_axis = 0;
    static constexpr std::size_t y_axis = 1;

    std::array<T, 2> elements_;

    [[nodiscard]] static constexpr T abs_difference(T lhs, T rhs) noexcept
    {
        return std::max(lhs, rhs) - std::min(lhs, rhs);
    }

    [[nodiscard]] static constexpr T abs_difference_x(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return abs_difference(lhs.x(), rhs.x());
    }

    [[nodiscard]] static constexpr T abs_difference_y(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return abs_difference(lhs.y(), rhs.y());
    }

    [[nodiscard]] static constexpr Vec2<T> abs_difference(const Vec2<T>& lhs, const Vec2<T>& rhs) noexcept
    {
        return {abs_difference(lhs.x(), rhs.x()), abs_difference(lhs.y(), rhs.y())};
    }
};

template <typename Vec2Container>
[[nodiscard]] std::optional<typename Vec2Container::value_type::dimension_type> min_x(const Vec2Container& vec2s)
{
    if (vec2s.size() == 0) {
        return {};
    }
    return std::min_element(vec2s.cbegin(), vec2s.cend(), [](auto lhs, auto rhs) { return lhs.x() < rhs.x(); })->x();
}

template <typename Vec2Container>
[[nodiscard]] std::optional<typename Vec2Container::value_type::dimension_type> max_x(const Vec2Container& vec2s)
{
    if (vec2s.size() == 0) {
        return {};
    }
    return std::max_element(vec2s.cbegin(), vec2s.cend(), [](auto lhs, auto rhs) { return lhs.x() < rhs.x(); })->x();
}

template <typename Vec2Container>
[[nodiscard]] std::optional<typename Vec2Container::value_type::dimension_type> min_y(const Vec2Container& vec2s)
{
    if (vec2s.size() == 0) {
        return {};
    }
    return std::min_element(vec2s.cbegin(), vec2s.cend(), [](auto lhs, auto rhs) { return lhs.y() < rhs.y(); })->y();
}

template <typename Vec2Container>
[[nodiscard]] std::optional<typename Vec2Container::value_type::dimension_type> max_y(const Vec2Container& vec2s)
{
    if (vec2s.size() == 0) {
        return {};
    }
    return std::max_element(vec2s.cbegin(), vec2s.cend(), [](auto lhs, auto rhs) { return lhs.y() < rhs.y(); })->y();
}

template <typename Vec2Container>
[[nodiscard]] std::optional<typename Vec2Container::value_type> min_extent(const Vec2Container& vec2s)
{
    if (vec2s.size() == 0) {
        return {};
    }
    return {*min_x(vec2s), *min_y(vec2s)};
}

template <typename Vec2Container>
[[nodiscard]] std::optional<typename Vec2Container::value_type> max_extent(const Vec2Container& vec2s)
{
    if (vec2s.size() == 0) {
        return {};
    }
    return {*max_x(vec2s), *max_y(vec2s)};
}

template <typename Vec2Container>
[[nodiscard]] std::optional<std::pair<typename Vec2Container::value_type, typename Vec2Container::value_type>>
extents(const Vec2Container& vec2s)
{
    if (vec2s.size() == 0) {
        return {};
    }
    return {*min_extent(vec2s), *max_extent(vec2s)};
}

} // namespace dm
