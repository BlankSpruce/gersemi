use regex::Regex;
use std::iter::zip;

use crate::parser::quoted_argument_pattern;

pub fn remove_common_beginning(s: &str, other: &str) -> String {
    let mut index = 0;
    for (lhs, rhs) in zip(s.chars(), other.chars()) {
        if lhs != rhs {
            break;
        }
        index += 1;
    }

    s[index..].to_string()
}

pub fn strip_empty_lines_from_edges(s: &str) -> String {
    let mut result = s
        .lines()
        .skip_while(|x| x.trim().is_empty())
        .collect::<Vec<&str>>()
        .into_iter()
        .rev()
        .skip_while(|x| x.trim().is_empty())
        .collect::<Vec<&str>>();
    result.reverse();
    result.join("\n")
}

pub fn ends_with_line_comment(s: &str) -> bool {
    let mut start = 0;
    loop {
        let line_comment_begin_index = s[start..].rfind('#');
        match line_comment_begin_index {
            None => {
                return false;
            }
            Some(index) => {
                let bracket_comment_begin_index = s[start..].rfind("#[");
                if bracket_comment_begin_index == Some(index) {
                    start = index + 1;
                } else {
                    return true;
                }
            }
        }
    }
}

fn flat_split(pattern: &str, s: &str) -> (String, Option<[String; 2]>) {
    let regex = Regex::new(pattern).unwrap();
    match regex.find(s) {
        None => (s.to_string(), None),
        Some(m) => (
            s[..m.start()].to_string(),
            Some([s[m.range()].to_string(), s[m.end()..].to_string()]),
        ),
    }
}

fn split_by_line_comment(s: &str) -> (String, Option<[String; 2]>) {
    flat_split(r"\s*#", s)
}

fn split_by_bracket_arguments(s: &str) -> (String, Option<[String; 2]>) {
    let regex_start = Regex::new(r"\[(=*)\[").unwrap();
    if let Some(captures) = regex_start.captures(s) {
        if let Some(matched_left_bracket) = captures.get(1) {
            let equal_signs = "=".repeat(matched_left_bracket.len());
            let pattern = format!(r"\[{equal_signs}\[([\s\S]+?)\]{equal_signs}\]");
            return flat_split(&pattern, s);
        }
    }

    (s.to_string(), None)
}

fn split_by_quoted_arguments(s: &String) -> Vec<String> {
    let regex = Regex::new(quoted_argument_pattern()).unwrap();
    let mut s: &str = s;
    let mut result = Vec::<String>::new();
    while let Some(matched) = regex.find(s) {
        result.push(s[..matched.start()].to_string());
        result.push(s[matched.range()].to_string());
        s = &s[matched.end()..];
    }
    result.push(s.to_string());
    result
}

fn split_into_segments(s: &str) -> Vec<String> {
    let (head, comment) = split_by_line_comment(s);
    let line_comment = match comment {
        None => String::new(),
        Some(comment) => comment.into_iter().collect::<String>(),
    };

    let (head, line_comment) = if head.contains('"') {
        (format!("{head}{line_comment}"), String::new())
    } else {
        (head, line_comment)
    };

    let segments = split_by_bracket_arguments(&head);
    let segments = match segments {
        (front, None) => vec![split_by_quoted_arguments(&front), vec![line_comment]],
        (front, Some([middle, back])) => vec![
            split_by_quoted_arguments(&front),
            split_by_quoted_arguments(&middle),
            split_by_quoted_arguments(&back),
            vec![line_comment],
        ],
    };

    let mut result = Vec::<String>::new();
    for segment in segments {
        for item in segment {
            if !item.is_empty() {
                result.push(item);
            }
        }
    }
    result
}

fn indent<Predicate: Fn(&str) -> bool>(
    s: &str,
    indent_symbol: &str,
    predicate: Predicate,
) -> String {
    s.split_inclusive('\n')
        .map(|line| {
            if predicate(line) {
                format!("{indent_symbol}{line}")
            } else {
                line.to_string()
            }
        })
        .collect::<String>()
}

fn indent_segment(segment: &str, indent_symbol: &str) -> String {
    if segment.starts_with('[')
        || segment.starts_with('"')
        || segment.starts_with(' ')
        || segment.starts_with('\t')
    {
        return segment.to_string();
    }

    indent(segment, indent_symbol, |x| !x.starts_with('\n'))
}

pub fn safe_indent(s: &str, indent_symbol: &str) -> String {
    let result = split_into_segments(s)
        .into_iter()
        .map(|x| indent_segment(&x, indent_symbol))
        .collect::<Vec<String>>();
    result.into_iter().collect::<String>()
}
