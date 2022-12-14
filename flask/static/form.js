$(document).ready(function() {
  $('#new_investment_form').on('submit', function(event) {
    $.ajax({
      data : {
        new_investment : $('#new_investment').val(),
        odds_a : $('#investment_odds_a').val(),
        odds_b : $('#investment_odds_b').val(),
        odds_draw : $('#investment_odds_draw').val()
      },
      type: 'POST',
      url : '/new_investment'
    }).done(function(data) {
      $('#profit_cell').text(data.profit);
      $('#to_bet_a_cell').text(data.to_bet_a);
      $('#to_bet_b_cell').text(data.to_bet_b);
      $('#to_bet_draw_cell').text(data.to_bet_draw);
    });

    event.preventDefault();
  });

  $('button').on('click', function(event) {
    $.ajax({
      data : {
        select_arb_index : event.target.value
      },
      type: 'POST',
      url : '/select_arb'
    }).done(function(data) {
      $('#team_a_cell').text(data.team_a);
      $('#team_b_cell').text(data.team_b);
      $('#bookmaker_a_cell').text(data.bookmaker_a);
      $('#bookmaker_b_cell').text(data.bookmaker_b);
      $('#odds_a_cell').text(data.odds_a);
      $('#odds_b_cell').text(data.odds_b);
      $('#category_cell').text(data.category);
      $('#commence_time_cell').text(data.start_time);

      $('#profit_cell').text(data.profit);
      $('#to_bet_a_cell').text(data.to_bet_a);
      $('#to_bet_b_cell').text(data.to_bet_b);

      $('#investment_odds_a').val(data.odds_a);
      $('#investment_odds_b').val(data.odds_b);

      $('#bookmaker_draw_cell').text(data.bookmaker_draw);
      $('#odds_draw_cell').text(data.odds_draw);
      $('#to_bet_draw_cell').text(data.to_bet_draw);
      $('#investment_odds_draw').val(data.odds_draw);
    });

    event.preventDefault();
  });
});